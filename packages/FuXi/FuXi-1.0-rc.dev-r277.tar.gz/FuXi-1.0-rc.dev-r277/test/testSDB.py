#!/bin/env python
import unittest, os, time, sys, urllib
from pprint import pprint
from cStringIO import StringIO
from FuXi.Rete.Proof import GenerateProof
from FuXi.Syntax.InfixOWL import *
from FuXi.Horn import ComplementExpansion
from FuXi.Rete.Network import ReteNetwork
from FuXi.Rete.RuleStore import N3RuleStore,SetupRuleStore
from FuXi.DLP import MapDLPtoNetwork, non_DHL_OWL_Semantics, makeRule, SKOLEMIZED_CLASS_NS
from FuXi.Rete.Util import generateTokenSet, renderNetwork
from rdflib.util import first
from rdflib.Literal import _XSD_NS
from rdflib.Collection import Collection
from rdflib import URIRef, RDF, RDFS, Namespace, Variable, Literal, URIRef
from rdflib.syntax.NamespaceManager import NamespaceManager
from rdflib.Graph import ConjunctiveGraph, Graph, ReadOnlyGraphAggregate, Namespace

EX = Namespace('http://example.com#')
DNODE=Namespace('http://www.clevelandclinic.org/heartcenter/ontologies/DataNodes.owl#')

class DisjunctionOperatorTest(unittest.TestCase):
    def setUp(self):
        self.domainModelGraph=Graph().parse('../../../../SemanticDB/OntologyManager/testing/containsAlias.rdf')
        self.closureDeltaGraph=Graph()
        self.ruleStore,self.ruleGraph=SetupRuleStore()
        print self.domainModelGraph.serialize(format='n3')
        self.network = ReteNetwork(self.ruleStore,
                                   inferredTarget = self.closureDeltaGraph,)
                                   #nsMap = self.ruleStore.nsMgr)
        self.network.parseN3Logic(open('../../../../SemanticDB/OntologyManager/ptrecRules.n3'))
        self.network.feedFactsToAdd(generateTokenSet(self.domainModelGraph))

    def test1(self):
        print self.domainModelGraph.serialize(format='n3')
        self.failUnless((DNODE.DataNodeModel,None,None) in self.closureDeltaGraph, "Missing assertions about dnode:DataNodeModel")
    
if __name__ == '__main__':
    unittest.main()