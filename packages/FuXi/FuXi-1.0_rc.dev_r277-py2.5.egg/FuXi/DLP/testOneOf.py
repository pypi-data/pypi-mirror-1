#!/bin/env python
import unittest, os, time, sys
from cStringIO import StringIO
from FuXi.Syntax.InfixOWL import *
from FuXi.Horn import ComplementExpansion
from FuXi.Rete import ReteNetwork
from FuXi.Rete.RuleStore import N3RuleStore
from FuXi.DLP import MapDLPtoNetwork, non_DHL_OWL_Semantics
from FuXi.Rete.Proof import GenerateProof
from FuXi.Rete.Util import generateTokenSet, renderNetwork
from rdflib import URIRef, RDF, RDFS
from rdflib.syntax.NamespaceManager import NamespaceManager
from rdflib.Graph import ConjunctiveGraph, Graph, ReadOnlyGraphAggregate, Namespace

HEART_NS           = Namespace('tag:info@semanticdb.ccf.org,2007:HVICoreDataElements#')
PTREC_NS           = Namespace('tag:info@semanticdb.ccf.org,2007:PatientRecordTerms#')

ONE_OF_AXIOMS_2=\
"""<?xml version="1.0"?>
<!DOCTYPE rdf:RDF [
    <!ENTITY heart "tag:info@semanticdb.ccf.org,2007:HVICoreDataElements#" >
    <!ENTITY sts "tag:info@semanticdb.ccf.org,2008:STS.2.61#" >
    <!ENTITY ptrec "tag:info@semanticdb.ccf.org,2007:PatientRecordTerms#" >
    <!ENTITY dnode "http://www.clevelandclinic.org/heartcenter/ontologies/DataNodes.owl#" >
]>
<rdf:RDF 
     xmlns:dnode="&dnode;"
     xmlns:ptrec="tag:info@semanticdb.ccf.org,2007:PatientRecordTerms#"
     xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
     xmlns:owl="http://www.w3.org/2002/07/owl#"
     xmlns:skos="http://www.w3.org/2004/02/skos/core#"
     xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <owl:Class rdf:about="&ptrec;VADInsertion">
        <skos:editorialNote>Implemented using DLP / n3-horn</skos:editorialNote>
        <owl:intersectionOf rdf:parseType="Collection">
            <rdf:Description rdf:about="&ptrec;SurgicalProcedure_assist_device_assist_device_insertion"/>
            <owl:Restriction>
                <owl:onProperty rdf:resource="&dnode;contains"/>
                <owl:someValuesFrom>
                    <owl:Class>
                        <owl:intersectionOf rdf:parseType="Collection">
                            <owl:Restriction>
                                <owl:onProperty rdf:resource="&dnode;contains"/>
                                <owl:someValuesFrom>
                                    <owl:Class>
                                        <owl:intersectionOf rdf:parseType="Collection">
                                            <rdf:Description rdf:about="&ptrec;CardiacAssistDevice"/>
                                            <owl:Restriction>
                                                <owl:onProperty rdf:resource="&ptrec;hasCardiacAssistDeviceType"/>
                                                <owl:someValuesFrom>
                                                    <owl:Class>
                                                        <owl:oneOf rdf:parseType="Collection">
                                                            <rdf:Description rdf:about="&ptrec;CardiacAssistDeviceType_percutaneous_ventricular_assist"/>
                                                        </owl:oneOf>
                                                    </owl:Class>
                                                </owl:someValuesFrom>
                                            </owl:Restriction>
                                        </owl:intersectionOf>
                                    </owl:Class>
                                </owl:someValuesFrom>
                            </owl:Restriction>
                            <rdf:Description rdf:about="&ptrec;CardiacAssistDeviceInsertion"/>
                        </owl:intersectionOf>
                    </owl:Class>
                </owl:someValuesFrom>
            </owl:Restriction>
        </owl:intersectionOf>
        <rdfs:subClassOf rdf:resource="&sts;VADInsertion"/>
    </owl:Class>
</rdf:RDF>"""

OWL_1=\
"""<?xml version="1.0"?>
<!DOCTYPE rdf:RDF [
    <!ENTITY heart "tag:info@semanticdb.ccf.org,2007:HVICoreDataElements#" >
    <!ENTITY sts "tag:info@semanticdb.ccf.org,2008:STS.2.61#" >
    <!ENTITY ptrec "tag:info@semanticdb.ccf.org,2007:PatientRecordTerms#" >
    <!ENTITY dnode "http://www.clevelandclinic.org/heartcenter/ontologies/DataNodes.owl#" >
    <!ENTITY csqr "tag:info@semanticdb.ccf.org,2008:CardiacSurgeryQualityReport#" >
]>
<rdf:RDF
    xmlns:dnode="&dnode;"
    xmlns:ptrec="tag:info@semanticdb.ccf.org,2007:PatientRecordTerms#"
    xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
    xmlns:owl="http://www.w3.org/2002/07/owl#"
    xmlns:skos="http://www.w3.org/2004/02/skos/core#"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <owl:Class rdf:about="&sts;ReoperationForBleeding">
        <owl:intersectionOf rdf:parseType="Collection">
            <owl:Class>
                <owl:intersectionOf rdf:parseType="Collection">
                    <rdf:Description rdf:about="&ptrec;Event_management_operation"/>
                    <owl:Restriction>
                        <owl:onProperty rdf:resource="&dnode;contains"/>
                        <owl:someValuesFrom rdf:resource="&ptrec;SurgicalProcedure_thoracic_control_bleeding"/>
                    </owl:Restriction>
                </owl:intersectionOf>
            </owl:Class>
            <rdf:Description rdf:about="&csqr;PostOpInHospitalEvent"/>
        </owl:intersectionOf>
    </owl:Class> 
</rdf:RDF>"""

OWL_2=\
"""
<!DOCTYPE rdf:RDF [
    <!ENTITY heart "tag:info@semanticdb.ccf.org,2007:HVICoreDataElements#" >
    <!ENTITY sts "tag:info@semanticdb.ccf.org,2008:STS.2.61#" >
    <!ENTITY ptrec "tag:info@semanticdb.ccf.org,2007:PatientRecordTerms#" >
    <!ENTITY dnode "http://www.clevelandclinic.org/heartcenter/ontologies/DataNodes.owl#" >
    <!ENTITY csqr "tag:info@semanticdb.ccf.org,2008:CardiacSurgeryQualityReport#" >
]>
<rdf:RDF
    xmlns:dnode="&dnode;"
    xmlns:ptrec="tag:info@semanticdb.ccf.org,2007:PatientRecordTerms#"
    xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
    xmlns:owl="http://www.w3.org/2002/07/owl#"
    xmlns:skos="http://www.w3.org/2004/02/skos/core#"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <owl:Class rdf:about="&heart;AorticAneurysmRepair">
        <rdfs:subClassOf rdf:resource="&sts;AorticAneurysmRepair"/>
    </owl:Class>    
</rdf:RDF>"""

class OWLDLPTest(unittest.TestCase):
    def setUp(self):
        nsMgr = NamespaceManager(Graph())
        nsMgr.bind(u'ptrec',PTREC_NS)
        self.tBoxGraph = Graph(namespace_manager=nsMgr).parse(StringIO(OWL_1))
        Individual.factoryGraph = self.tBoxGraph 
#        self.factGraph=Graph().parse('40074929.rdf')
        
    def testRuleStore(self):
        network = ReteNetwork(N3RuleStore())
        network.getNsBindings(self.tBoxGraph.namespace_manager)
        NominalRangeTransformer().transform(self.tBoxGraph)
        list(MapDLPtoNetwork(network,self.tBoxGraph))
        for tNode in network.terminalNodes:
            print tNode.clause.n3()
        print network

class NominalRangeTransformer(object):        
    NOMINAL_QUERY=\
    """SELECT ?RESTRICTION ?INTERMEDIATE_CLASS ?NOMINAL ?PROP
       { ?RESTRICTION owl:onProperty ?PROP;
                      owl:someValuesFrom ?INTERMEDIATE_CLASS .  
         ?INTERMEDIATE_CLASS owl:oneOf ?NOMINAL .  } """    
    
    def transform(self,graph):
        """
        Transforms a 'pure' nominal range into a disjunction of value restrictions
        """
        Individual.factoryGraph = graph
        for restriction,intermediateCl,nominal,prop in graph.query(
                                 self.NOMINAL_QUERY,
                                 initNs={u'owl':OWL_NS}):
            nominalCollection=Collection(graph,nominal)
            #purge restriction
            graph.remove((restriction,None,None))
            newConjunct=BooleanClass(restriction,
                                     OWL_NS.unionOf,
                                     [Property(prop)|value|val 
                                                 for val in nominalCollection],
                                     graph)
            #purge nominalization placeholder
            graph.remove((intermediateCl,None,None))
            nominalCollection.clear()
            graph.remove((nominal,None,None))
            print "..Transformed a nominal relation range to a disjunction of value restrictions.."

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
#        print self.tBoxGraph.serialize(format='turtle')
        _class=Class(PTREC_NS.VADInsertion)
#        print _class.__repr__(True)
#        for restr in self.tBoxGraph.subjects(predicate=OWL_NS.hasValue):
#            print "owl:hasValue restriction: %s %s"%(restr,manchesterSyntax(restr,self.tBoxGraph))
        list(MapDLPtoNetwork(network,self.tBoxGraph))
#        renderNetwork(network,nsMap=network.nsMap).write_jpeg('oneOfNetwork.jpg')
        for tNode in network.terminalNodes:
            print tNode.clause.n3()
        network.feedFactsToAdd(generateTokenSet(self.factGraph))
        print network
#        network.reportConflictSet(True)
        vadIns=first(network.inferredFacts.subjects(predicate=RDF.type,object=_class.identifier))
        self.failUnless(vadIns is None, "There should be no ptrec:VADInsertions!")
#        builder,proof=GenerateProof(network,
#                                    (vadIns,RDF.type,_class.identifier))
#        for entry in builder.trace:
#            print entry
#        builder.renderProof(proof).write_jpeg('oneOfProofTree.jpg')

if __name__ == "__main__":
    unittest.main()
