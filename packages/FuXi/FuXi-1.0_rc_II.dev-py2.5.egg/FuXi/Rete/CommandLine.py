#!/usr/bin/env python
from pprint import pprint
from FuXi.Rete.Proof import GenerateProof
from FuXi.Rete import ReteNetwork
from FuXi.Rete.AlphaNode import SUBJECT,PREDICATE,OBJECT,VARIABLE
from FuXi.Rete.BetaNode import PartialInstanciation, LEFT_MEMORY, RIGHT_MEMORY
from FuXi.Rete.RuleStore import N3RuleStore, SetupRuleStore
from FuXi.Rete.Util import renderNetwork,generateTokenSet, xcombine
from FuXi.DLP.DLNormalization import NormalFormReduction
from FuXi.DLP import MapDLPtoNetwork, non_DHL_OWL_Semantics, DisjunctiveNormalForm
from FuXi.Horn import *
from FuXi.Horn.HornRules import HornFromN3, Ruleset
from FuXi.Syntax.InfixOWL import *
from FuXi.Rete.TopDown import *
from FuXi.Rete.Proof import ProofBuilder, PML, GMP_NS
from FuXi.Rete.Magic import *
from FuXi.Rete.SidewaysInformationPassing import *
from rdflib.sparql.bison.Query import Prolog
from rdflib.Namespace import Namespace
from rdflib import plugin,RDF,RDFS,URIRef,URIRef,Literal,Variable
from rdflib.store import Store
from cStringIO import StringIO
from rdflib.Graph import Graph,ReadOnlyGraphAggregate,ConjunctiveGraph
from rdflib.syntax.NamespaceManager import NamespaceManager
import unittest, time, warnings,sys

TEMPLATES = Namespace('http://code.google.com/p/fuxi/wiki/BuiltinSPARQLTemplates#')

def main():
    from optparse import OptionParser
    op = OptionParser('usage: %prog [options] factFile1 factFile2 ... factFileN')
    op.add_option('--why', 
                  action='append',
                  default=[],
      help = 'Used with --filter to solve queries (the heads of filter-rules) '+
             'in a top-down fashion using the adorned program and sip for each rule '+
             'In this way OWL-DLP, OWL2-RL, N3, (and RIF) theories can be solved / queried')    
    op.add_option('--closure', 
                  action='store_true',
                  default=False,
      help = 'Whether or not to serialize the inferred triples'+ 
             ' along with the original triples.  Otherwise '+
              '(the default behavior), serialize only the inferred triples')
    op.add_option('--output', 
                  default='n3',
                  metavar='RDF_FORMAT',
                  choices = ['xml', 
                             'TriX', 
                             'n3', 
                             'pml',
                             'proof-graph',
                             'nt',
                             'rif',
                             'rif-xml',
                             'conflict',
                             'man-owl'],
      help = "Serialize the inferred triples and/or original RDF triples to STDOUT "+
             "using the specified RDF syntax ('xml','pretty-xml','nt','turtle', "+
             "or 'n3') or to print a summary of the conflict set (from the RETE "+
             "network) if the value of this option is 'conflict'.  If the the "+
             " value is 'rif' or 'rif-xml', Then the rules used for inference "+
             "will be serialized as RIF.  If the value is 'pml' and --why is used, "+
             " then the PML RDF statements are serialized.  If output is "+
             "'proof-graph then a graphviz .dot file of the proof graph is printed. "+
             "Finally if the value is 'man-owl', then the RDF facts are assumed "+
             "to be OWL/RDF and serialized via Manchester OWL syntax. The default is %default")
    op.add_option('--class',
                  dest='classes',
                  action='append',
                  default=[],
                  metavar='QNAME', 
      help = 'Used with --output=man-owl to determine which '+
             'classes within the entire OWL/RDF are targetted for serialization'+
             '.  Can be used more than once')
    op.add_option('--property',
                  action='append',
                  dest='properties',
                  default=[],
                  metavar='QNAME', 
      help = 'Used with --output=man-owl or --extract to determine which '+
             'properties are serialized / extracted.  Can be used more than once')
    op.add_option('--normalize', 
                  action='store_true',
                  default=False,
      help = "Used with --output=man-owl to attempt to determine if the ontology is 'normalized' [Rector, A. 2003]"+
      "The default is %default")
    op.add_option('--input-format', 
                  default='xml',
                  dest='inputFormat',
                  metavar='RDF_FORMAT',
                  choices = ['xml', 'trix', 'n3', 'nt', 'rdfa'],
      help = "The format of the RDF document(s) which serve as the initial facts "+
             " for the RETE network. One of 'xml','n3','trix', 'nt', "+
             "or 'rdfa'.  The default is %default")
    op.add_option('--safety', 
                  default='none',
                  metavar='RULE_SAFETY',
                  choices = ['loose', 'strict','none'],
      help = "Determines how to handle RIF Core safety.  A value of 'loose' "+
             " means that unsafe rules will be ignored.  A value of 'strict' "+
             " will cause a syntax exception upon any unsafe rule.  A value of "+
             "'none' (the default) does nothing")    
    op.add_option('--pDSemantics', 
                  action='store_true',
                  default=False,
      help = 'Used with --dlp to add pD semantics ruleset for semantics not covered '+
      'by DLP but can be expressed in definite Datalog Logic Programming'+
      ' The default is %default')
    op.add_option('--stdin', 
                  action='store_true',
                  default=False,
      help = 'Parse STDIN as an RDF graph to contribute to the initial facts. The default is %default ')
    op.add_option('--ns', 
                  action='append',
                  default=[],
                  metavar="PREFIX=URI",
      help = 'Register a namespace binding (QName prefix to a base URI).  This '+
             'can be used more than once')
    op.add_option('--rules', 
                  default=[],
                  action='append',
                  metavar='PATH_OR_URI',
      help = 'The Notation 3 documents to use as rulesets for the RETE network'+
      '.  Can be specified more than once')
    op.add_option('-d', '--debug', action='store_true',default=False,
      help = 'Include debugging output')
    op.add_option('--strictness',
                  default='defaultBase',
                  metavar='DDL_STRICTNESS',
                  choices = ['loose', 
                             'defaultBase', 
                             'defaultDerived', 
                             'harsh'],
      help = 'Used with --why to specify whether to: *not* check if predicates are '+
      ' both derived and base (loose), if they are, mark as derived (defaultDerived) '+
      'or as base (defaultBase) predicates, else raise an exception (harsh)')    
    op.add_option('--method',
                  default='bottomUp',
                  metavar='evaluation method',
                  choices = ['bottomUp', 'topDown','both'],
      help = 'Used with --why to specify how to evaluate answers for query.  '+
      'Either both (default), top-down alone, or bottom-up alone')        
    op.add_option('--firstAnswer',
                  default=False,
                  action='store_true',
      help = 'Used with --why to determine whether to fetch all answers or just '+
      'the first')            
    op.add_option('--edb',
                  default=[],
                  action='append',
                  metavar='EXTENSIONAL_DB_PREDICATE_QNAME',                  
      help = 'Used with --why/--strictness=defaultDerived to specify which clashing '+
      'predicate will be designated as a base predicate')
    op.add_option('--idb',
                  default=[],
                  action='append',
                  metavar='INTENSIONAL_DB_PREDICATE_QNAME',                  
      help = 'Used with --why/--strictness=defaultBase to specify which clashing '+
      'predicate will be designated as a derived predicate')                    
    op.add_option('--filter', 
                  action='append',
                  default=[],
                  metavar='PATH_OR_URI',
      help = 'The Notation 3 documents to use as a filter (entailments do not particpate in network)')
    op.add_option('--ruleFacts', 
                  action='store_true',
                  default=False,
      help = "Determines whether or not to attempt to parse initial facts from "+
      "the rule graph.  The default is %default")
    op.add_option('--builtins', 
                  default=False,
                  metavar='PATH_TO_PYTHON_MODULE',
      help = "The path to a python module with function definitions (and a "+
      "dicitonary called ADDITIONAL_FILTERS) to use for builtins implementations")    
    op.add_option('--dlp', 
                  action='store_true',
                  default=False,
      help = 'Use Description Logic Programming (DLP) to extract rules from OWL/RDF.  The default is %default')
    op.add_option('--ontology', 
                  action='append',
                  default=[],
                  metavar='PATH_OR_URI',
      help = 'The path to an OWL RDF/XML graph to use DLP to extract rules from '+
      '(other wise, fact graph(s) are used)  ')    
    op.add_option('--builtinTemplates', 
                  default=None,
                  metavar='N3_DOC_PATH_OR_URI',
      help = 'The path to an N3 document associating SPARQL FILTER templates to '+
      'rule builtins')        
    op.add_option('--negation', 
                  action='store_true',
                  default=False,                
      help = 'Extract negative rules?')    
    op.add_option('--normalForm', 
                  action='store_true',
                  default=False,                
      help = 'Whether or not to reduce DL axioms & LP rules to a normal form')        
    (options, facts) = op.parse_args()
    
    nsBinds = {'iw':'http://inferenceweb.stanford.edu/2004/07/iw.owl#'}
    for nsBind in options.ns:
        pref,nsUri = nsBind.split('=')
        nsBinds[pref]=nsUri
    
    namespace_manager = NamespaceManager(Graph())
    factGraph = Graph() 
    ruleSet = Ruleset()

    for fileN in options.rules:
        if options.ruleFacts:
            factGraph.parse(fileN,format='n3')
            print >>sys.stderr,"Parsing RDF facts from ", fileN
        if options.builtins:
            import imp
            userFuncs = imp.load_source('builtins', options.builtins)
            rs = HornFromN3(fileN,
                            additionalBuiltins=userFuncs.ADDITIONAL_FILTERS)
        else:
            rs = HornFromN3(fileN)
        nsBinds.update(rs.nsMapping)
        ruleSet.formulae.extend(rs)
        #ruleGraph.parse(fileN,format='n3')

    ruleSet.nsMapping = nsBinds

    for prefix,uri in nsBinds.items():
        namespace_manager.bind(prefix, uri, override=False)
    closureDeltaGraph = Graph()
    closureDeltaGraph.namespace_manager = namespace_manager
    factGraph.namespace_manager = namespace_manager

    for fileN in facts:
        factGraph.parse(fileN,format=options.inputFormat)
        
    if facts:
        for pref,uri in factGraph.namespaces():
            nsBinds[pref]=uri
        
    if options.stdin:
        factGraph.parse(sys.stdin,format=options.inputFormat)
        
    #Normalize namespace mappings
    #prune redundant, rdflib-allocated namespace prefix mappings
    newNsMgr = NamespaceManager(factGraph)
    from FuXi.Rete.Util import CollapseDictionary    
    for k,v in CollapseDictionary(dict([(k,v) 
                                    for k,v in factGraph.namespaces()])).items():
        newNsMgr.bind(k,v)
    factGraph.namespace_manager = newNsMgr
        
    if options.normalForm:
        NormalFormReduction(factGraph)
                
    workingMemory = generateTokenSet(factGraph)
    if options.builtins:
        import imp
        userFuncs = imp.load_source('builtins', options.builtins)
        rule_store, rule_graph, network = SetupRuleStore(
                             makeNetwork=True,
                             additionalBuiltins=userFuncs.ADDITIONAL_FILTERS)
    else:
        rule_store, rule_graph, network = SetupRuleStore(makeNetwork=True)
    network.inferredFacts = closureDeltaGraph
    network.nsMap = nsBinds
    
    if options.dlp:
        from FuXi.DLP.DLNormalization import NormalFormReduction
        if options.ontology:
            ontGraph = Graph()
            for fileN in options.ontology:
                ontGraph.parse(fileN)
             
        else:
            ontGraph=factGraph
        NormalFormReduction(ontGraph)
        dlp=network.setupDescriptionLogicProgramming(
                                 ontGraph,
                                 addPDSemantics=options.pDSemantics,
                                 constructNetwork=False,
                                 ignoreNegativeStratus=options.negation,
                                 safety = safetyNameMap[options.safety]) 
        ruleSet.formulae.extend(dlp)
    if options.output == 'rif' and not options.why:
        for rule in ruleSet:
            print rule
        if options.negation:
            for nRule in network.negRules:
                print nRule
        
    elif options.output == 'man-owl':
        cGraph = network.closureGraph(factGraph,readOnly=False)
        cGraph.namespace_manager = namespace_manager
        Individual.factoryGraph = cGraph
        if options.classes:
            mapping = dict(namespace_manager.namespaces())
            for c in options.classes:
                pref,uri=c.split(':')
                print Class(URIRef(mapping[pref]+uri)).__repr__(True)
        elif options.properties:
            mapping = dict(namespace_manager.namespaces())
            for p in options.properties:
                pref,uri=p.split(':')
                print Property(URIRef(mapping[pref]+uri))
        else:
            for p in AllProperties(cGraph):
                print p.identifier
                print repr(p)
            for c in AllClasses(cGraph):
                if options.normalize:
                    if c.isPrimitive():
                        primAnc = [sc for sc in c.subClassOf if sc.isPrimitive()] 
                        if len(primAnc)>1:
                            warnings.warn("Branches of primitive skeleton taxonomy"+
                              " should form trees: %s has %s primitive parents: %s"%(
                             c.qname,len(primAnc),primAnc),UserWarning,1)
                        children = [desc for desc in c.subSumpteeIds()]
                        for child in children:
                            for otherChild in [o for o in children if o is not child]:
                                if not otherChild in [c.identifier 
                                          for c in Class(child).disjointWith]:# and\
                                    warnings.warn("Primitive children (of %s) "+
                                          "must be mutually disjoint: %s and %s"%(
                                      c.qname,
                                      Class(child).qname,
                                      Class(otherChild).qname),UserWarning,1)
#                if not isinstance(c.identifier,BNode):
                print c.__repr__(True)
                    
    if not options.why:
        #Niave construction of graph
        for rule in ruleSet:
            network.buildNetworkFromClause(rule)

    magicSeeds=[]
    if options.why:
        try:
            from rdflib.sparql.parser import parse as ParseSPARQL
            from rdflib.sparql.Algebra import ReduceGraphPattern
        except:
            from rdflib.sparql.bison.Processor import Parse as ParseSPARQL
            from rdflib.sparql.Algebra import ReduceGraphPattern
        
        builtinTemplateGraph = Graph()
        if options.builtinTemplates:
            builtinTemplateGraph = Graph().parse(options.builtinTemplates,
                                                format='n3')
        factGraph.templateMap = \
            dict([(pred,template)
                      for pred,_ignore,template in 
                            builtinTemplateGraph.triples(
                                (None,
                                 TEMPLATES.filterTemplate,
                                 None))])
        goals=[]
        for query in options.why:
            query = ParseSPARQL(query) 
            network.nsMap['pml'] = PML
            network.nsMap['gmp'] = GMP_NS
            network.nsMap['owl'] = OWL_NS        
            nsBinds.update(network.nsMap)
            network.nsMap = nsBinds
            if not query.prolog:
                    query.prolog = Prolog(None, [])
                    query.prolog.prefixBindings.update(nsBinds)
            else:
                for prefix, nsInst in nsBinds.items():
                    if prefix not in query.prolog.prefixBindings:
                        query.prolog.prefixBindings[prefix] = nsInst
            goals.extend([(s,p,o) for s,p,o,c in ReduceGraphPattern(
                                        query.query.whereClause.parsedGraphPattern,
                                        query.prolog).patterns])
        dPreds=[]# p for s,p,o in goals ]
        magicRuleNo = 0
        if options.output == 'rif' and options.method == 'bottomUp':
            print >>sys.stderr,"Resulting Magic program: "
        bottomUpDerivedPreds = []
        topDownDerivedPreds  = []
        defaultBasePreds     = []
        defaultDerivedPreds  = []
        mapping = dict(newNsMgr.namespaces())
        for edb in options.edb: 
            pref,uri=edb.split(':')
            defaultBasePreds.append(URIRef(mapping[pref]+uri))
        for idb in options.idb: 
            pref,uri=idb.split(':')
            defaultDerivedPreds.append(URIRef(mapping[pref]+uri))
        defaultDerivedPreds.extend(set([p == RDF.type and o or p for s,p,o in goals]))
        if options.method in ['both','topDown']:
            _rules = options.negation and set(ruleSet).union(network.negRules) or \
                     ruleSet 
            ruleSet = set(DisjunctiveNormalForm(_rules,
                                                safetyNameMap[options.safety],
                                                network))
            #Reset list of derived predicates
            dPreds = []
            factGraph.adornedProgram = \
                SetupDDLAndAdornProgram(
                    factGraph,
                    ruleSet,
                    goals,
                    derivedPreds=topDownDerivedPreds,
                    strictCheck=nameMap[options.strictness],
                    defaultPredicates=(defaultBasePreds,
                                       defaultDerivedPreds))
            assert factGraph.adornedProgram,goals
            sipCollection=PrepareSipCollection(factGraph.adornedProgram)
            print >>sys.stderr,"Derived predicates (top-down)", [factGraph.qname(term) 
                                                 for term in topDownDerivedPreds]
            if options.output == 'rif':
                print >>sys.stderr,"Rules used for top-down evaluation"
                for clause in factGraph.adornedProgram:
                    print >>sys.stderr,clause.formula                    
            if options.debug and sipCollection:
                print >>sys.stderr,"Sideways Information Passing (sip) graph: "
                for sip in SIPRepresentation(sipCollection):
                    print >>sys.stderr,sip
            solutions = []
            for goal in goals:
                goalSeed=AdornLiteral(goal).makeMagicPred()
                print >>sys.stderr,"Magic seed fact (used in bottom-up evaluation)",goalSeed
                magicSeeds.append(goalSeed.toRDFTuple())
                start = time.time()
                if options.method in ['topDown','both']:
                    for derivedAnswer in \
                            SipStrategy(
                                       goal,
                                       sipCollection,
                                       factGraph,
                                       topDownDerivedPreds,
                                       network = network,
                                       debug=options.debug):
                        if derivedAnswer:
                            ans,ns = derivedAnswer
                            solutions.append((ans,ns))
                            sTime = time.time() - start
                            goalRepr = RDFTuplesToSPARQL([AdornLiteral(goal)], factGraph)
                            if sTime > 1:
                                sTimeStr = "%s seconds"%sTime
                            else:
                                sTime = sTime * 1000
                                sTimeStr = "%s milli seconds"%sTime                    
                            print >>sys.stderr,\
                "Time to reach answer %s via top-down SPARQL sip strategy: %s"%(ans,sTimeStr)
                            #print >>sys.stderr,ans
                            if options.firstAnswer:
                                break
                            else:
                                start = time.time()
                    if solutions:
                        builder=ProofBuilder(network)
                        if 'pml' in options.output:
                            pGraph = Graph()
                            CommonNSBindings(pGraph,network.nsMap)
                        for ans,ns in solutions:
                            if 'pml' in options.output:
                                ns.serialize(builder,pGraph) 
                            elif 'proof-graph' in options.output:    
                                builder.extractGoalsFromNode(ns)
                        if 'pml' in options.output:                
                            print pGraph.serialize(format='n3')
                        elif 'proof-graph' in options.output:
                            builder.renderProof(ns,nsMap = network.nsMap).write_jpg('owl-proof.jpg')
                            print open('owl-proof.jpg').read()
            
        if options.method in ['both','bottomUp']:
            for rule in MagicSetTransformation(
                                       factGraph,
                                       ruleSet,
                                       goals,
                                       derivedPreds=bottomUpDerivedPreds,
                                       strictCheck=nameMap[options.strictness],
                                       defaultPredicates=(defaultBasePreds,
                                                          defaultDerivedPreds)):
                magicRuleNo+=1
                if options.output == 'rif' and options.method == 'bottomUp':
                    print >>sys.stderr, rule
                network.buildNetworkFromClause(rule)
            if len(ruleSet):
                print >>sys.stderr,"reduction in size of program: %s (%s -> %s clauses)"%(
                                           100-(float(magicRuleNo)/float(len(ruleSet)))*100,
                                           len(ruleSet),
                                           magicRuleNo)
            assert factGraph.adornedProgram
            print >>sys.stderr,"Derived predicates (bottom-up)", [factGraph.qname(term) 
                                                 for term in bottomUpDerivedPreds]            
            if options.output == 'rif':
                print >>sys.stderr,"Rules used for bottom-up evaluation"
                for clause in factGraph.adornedProgram:
                    print >>sys.stderr,clause.formula                    
                
    for fileN in options.filter:
        for rule in HornFromN3(fileN):
            network.buildFilterNetworkFromClause(rule)

    start = time.time()
    if options.why and options.method in ['both','bottomUp']:
       network.feedFactsToAdd(generateTokenSet(magicSeeds))
    if not options.why or options.method in ['both','bottomUp']: 
        network.feedFactsToAdd(workingMemory)
        sTime = time.time() - start
        if sTime > 1:
            sTimeStr = "%s seconds"%sTime
        else:
            sTime = sTime * 1000
            sTimeStr = "%s milli seconds"%sTime
        print >>sys.stderr,"Time to calculate closure on working memory: ",sTimeStr
        print >>sys.stderr, network
    if options.negation and network.negRules and options.method in ['both',
                                                                    'bottomUp']:
        now=time.time()      
        rt=network.calculateStratifiedModel(factGraph)
        print >>sys.stderr,\
        "Time to calculate stratified, stable model (inferred %s facts): %s"%(
                                    rt,
                                    time.time()-now)                
    if options.filter:
        print >>sys.stderr,"Applying filter to entailed facts"
        network.inferredFacts = network.filteredFacts


    if not options.why or options.method in ['both','bottomUp']:
        if options.output == 'conflict':
            network.reportConflictSet()
        elif options.output not in ['rif',
                                    'rif-xml',
                                    'man-owl',
                                    'pml',
                                    'proof-graph']:
            if options.closure:
                cGraph = network.closureGraph(factGraph)
                cGraph.namespace_manager = namespace_manager
                print cGraph.serialize(destination=None, 
                                       format=options.output, 
                                       base=None)
            elif options.output:
                print network.inferredFacts.serialize(destination=None, 
                                                      format=options.output, 
                                                      base=None)
            
if __name__ == '__main__':
    from hotshot import Profile, stats
#    import pycallgraph
#    pycallgraph.start_trace()
#    main()
#    pycallgraph.make_dot_graph('FuXi-timing.png')
#    sys.exit(1)
    p = Profile('fuxi.profile')
    p.runcall(main)
    p.close()    
    s = stats.load('fuxi.profile')
    s.strip_dirs()
    s.sort_stats('time','cumulative','pcalls')
    s.print_stats(.05)
    s.print_callers(.01)
    s.print_callees(.01)            