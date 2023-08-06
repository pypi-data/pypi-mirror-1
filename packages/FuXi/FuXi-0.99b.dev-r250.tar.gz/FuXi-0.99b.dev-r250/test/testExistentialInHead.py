import unittest, os, time, sys

N3_PROGRAM=\
"""
@prefix ptrec: <tag:info@semanticdb.ccf.org,2007:PatientRecordTerms#>.
@prefix dnode: <http://www.clevelandclinic.org/heartcenter/ontologies/DataNodes.owl#>.
@prefix owl:   <http://www.w3.org/2002/07/owl#>.
@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#>.
@prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#>.
@prefix csqr:  <tag:info@semanticdb.ccf.org,2008:CardiacSurgeryQualityReport#>.
@prefix str:   <http://www.w3.org/2000/10/swap/string#>.
@prefix log:   <http://www.w3.org/2000/10/swap/log#>.
@prefix cyc:   <http://sw.cyc.com/2006/07/27/cyc#>.
@prefix sts:   <tag:info@semanticdb.ccf.org,2008:STS.2.61#>.

{ ?HOSP a ptrec:Event_encounter_hospitalization; 
        dnode:contains ?HOSP_START_DATE, ?HOSP_STOP_DATE.  
  ?HOSP_START_DATE a ptrec:EventStartDate; ptrec:hasDateTimeMin ?ENCOUNTER_START.
  ?HOSP_STOP_DATE  a ptrec:EventStopDate; ptrec:hasDateTimeMax ?ENCOUNTER_STOP.
  ?EVT_DATE a ptrec:EventStartDate; ptrec:hasDateTimeMin ?EVT_START_MIN .
  ?EVT dnode:contains ?EVT_DATE ; a ?EVT_KIND .
  ?EVT_KIND log:notEqualTo ptrec:Event_encounter_hospitalization .
  ?EVT_START_MIN str:lessThan ?ENCOUNTER_STOP.
  ?EVT_START_MIN str:greaterThanOrEqualTo ?ENCOUNTER_START } => { ?EVT csqr:hasHospitalization ?HOSP } .
  

"""

class NominalRangeTransformTest(unittest.TestCase):
    def setUp(self):
        nsMgr = NamespaceManager(Graph())
        nsMgr.bind(u'ptrec',PTREC_NS)
        self.tBoxGraph = Graph(namespace_manager=nsMgr).parse(StringIO(ONE_OF_AXIOMS_2))
        Individual.factoryGraph = self.tBoxGraph 
        self.factGraph=Graph().parse('40074929.rdf')
        
    def testRuleStore(self):
        network = ReteNetwork(N3RuleStore())
        network.getNsBindings(self.tBoxGraph.namespace_manager)
        NominalRangeTransformer().transform(self.tBoxGraph)
        print self.tBoxGraph.serialize(format='turtle')
        _class=Class(PTREC_NS.VADInsertion)
#        for restr in self.tBoxGraph.subjects(predicate=OWL_NS.hasValue):
#            print "owl:hasValue restriction: %s %s"%(restr,manchesterSyntax(restr,self.tBoxGraph))
        list(MapDLPtoNetwork(network,self.tBoxGraph))
        for tNode in network.terminalNodes:
            print tNode.clause.n3()
        network.feedFactsToAdd(generateTokenSet(self.factGraph))
        print network
        network.reportConflictSet()
        vadIns=first(network.inferredFacts.subjects(predicate=RDF.type,object=_class.identifier))
        builder,proof=GenerateProof(network,
                                    (vadIns,RDF.type,_class.identifier))
#        for entry in builder.trace:
#            print entry
        builder.renderProof(proof).write_jpeg('oneOfProofTree.jpg')
        renderNetwork(network,nsMap=network.nsMap).write_jpeg('oneOfNetwork.jpg')

if __name__ == "__main__":
    unittest.main()
