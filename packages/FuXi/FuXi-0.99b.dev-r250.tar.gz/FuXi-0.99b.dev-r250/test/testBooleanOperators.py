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

class DisjunctionOperatorTest(unittest.TestCase):
    def setUp(self):
        self.tBoxGraph=Graph()
        self.tBoxGraph.namespace_manager.bind('ex',EX)
        self.tBoxGraph.namespace_manager.bind('owl',OWL_NS)
        Individual.factoryGraph = self.tBoxGraph
        self.classB = Class(EX.b)
        self.classE = Class(EX.e)
        self.classF = Class(EX.f) 
        self.classA = self.classE | self.classF
        self.classA.identifier = EX.a        
        self.classC = self.classA | self.classB
        self.classC.identifier = EX.c

    def testDisjunction(self):
        self.failUnless((EX.a,None,None) in self.tBoxGraph, "Missing assertions about %s"%EX.a)
        aList=Collection(self.tBoxGraph,EX.a)
        self.assertEquals(len(aList),2)
        for item in [EX.e,EX.f]:
            self.failUnless(item in aList, "Missing %s in %s"%(item,aList.n3()))
        self.failUnless((EX.c,None,None) in self.tBoxGraph, "Missing assertions about %s"%EX.c)
        cList=Collection(self.tBoxGraph,EX.c)
        self.assertEquals(len(cList),2)
        for item in [EX.a,EX.b]:
            self.failUnless(item in aList, "Missing %s in %s"%(item,cList.n3()))

    
if __name__ == '__main__':
    unittest.main()