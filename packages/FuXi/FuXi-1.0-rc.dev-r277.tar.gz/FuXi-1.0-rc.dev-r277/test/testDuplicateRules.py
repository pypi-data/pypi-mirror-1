import unittest, os, time, sys
from FuXi.Horn.PositiveConditions import And, Or, Uniterm, Condition, Atomic,SetOperator,Exists
from FuXi.Horn.HornRules import Clause
from rdflib import BNode, RDF, Namespace, Variable, RDFS, URIRef

SNO=Namespace('tag:info@ihtsdo.org,2007-07-31:SNOMED-CT#')

class NominalRangeTransformTest(unittest.TestCase):
    def setUp(self):
        pass
    
    def testRuleDuplicate(self):
        bN1 = BNode('plqJDAbW787')
        bN2 = BNode('plqJDAbW6934')
        head1 = And([Uniterm(RDF.type,[bN1,SNO.EntireHeart]),
                     Uniterm(SNO.partOf,[Variable('X'),bN1])])
        head2 = And([Uniterm(RDF.type,[bN2,SNO.EntireHeart]),
                     Uniterm(SNO.partOf,[Variable('X'),bN2])])
        commonBody = Uniterm(RDF.type,[Variable('X'),SNO.HeartPart])
        r1 = Clause(commonBody,Exists(head1,[bN1]))
        r2 = Clause(commonBody,Exists(head2,[bN2]))
        
        self.failUnlessEqual(r1,r2,"The BNodes should not count in syntactic equivalence!")
        
        bN1 = BNode('lSTVNgnt1363')
        bN2 = BNode('lSTVNgnt3553')
        head1 = And([Uniterm(RDF.type,[bN1,SNO.EntireBodyAsAWhole]),
                     Uniterm(SNO.partOf,[Variable('X'),bN1])])
        head2 = And([Uniterm(RDF.type,[bN2,SNO.EntireBodyAsAWhole]),
                     Uniterm(SNO.partOf,[Variable('X'),bN2])])
        commonBody = Uniterm(RDF.type,[Variable('X'),SNO.BodySystemStructure])
        r1 = Clause(commonBody,Exists(head1,[bN1]))
        r2 = Clause(commonBody,Exists(head2,[bN2]))

        self.failUnlessEqual(r1,r2,"The BNodes should not count in equivalence!")
        
        a=set([r1])
        self.failUnless(r1 in a,"The BNodes should not count in equivalence!")

if __name__ == "__main__":
    unittest.main()
