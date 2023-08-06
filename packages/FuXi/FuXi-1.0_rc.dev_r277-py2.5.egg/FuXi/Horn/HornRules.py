#!/usr/local/bin/python
# -*- coding: utf-8 -*-
"""
This section defines Horn rules for RIF Phase 1. The syntax and semantics 
incorporates RIF Positive Conditions defined in Section Positive Conditions
"""
from PositiveConditions import *
from rdflib import Variable, BNode, URIRef, Literal, Namespace,RDF,RDFS
from rdflib.Graph import Graph
def ExtractVariables(clause):
    pass

def HornFromN3(n3Stream):
    from FuXi.Rete.RuleStore import SetupRuleStore
    store,graph=SetupRuleStore(n3Stream)
    store._finalize()
    return Ruleset(n3Rules=store.rules,nsMapping=store.nsMgr)

def extractVariables(term,existential=True):
    if isinstance(term,existential and BNode or Variable):
        yield term
    elif isinstance(term,Uniterm):
        for t in term.toRDFTuple():
            if isinstance(t,existential and BNode or Variable):
                yield t
                
def iterCondition(condition):
    return isinstance(condition,SetOperator) and condition or iter([condition])
                
class Ruleset(object):
    """
    Ruleset ::= RULE*
    """
    def __init__(self,formulae=None,n3Rules=None,nsMapping=None):
        from FuXi.Rete.RuleStore import N3Builtin
        self.nsMapping = nsMapping and nsMapping or {}        
        self.formulae = formulae and formulae or []
        if n3Rules:
            from FuXi.DLP import breadth_first
            #Convert a N3 abstract model (parsed from N3) into a RIF BLD 
            for lhs,rhs in n3Rules:
                allVars = set()
                for ruleCondition in [lhs,rhs]:
                    for stmt in ruleCondition:
                        if isinstance(stmt,N3Builtin):
                            ExternalFunction(stmt,newNss=self.nsMapping)
#                            print stmt;raise
                        allVars.update([term for term in stmt if isinstance(term,(BNode,Variable))])
                body = [isinstance(term,N3Builtin) and term or
                         Uniterm(list(term)[1],[list(term)[0],list(term)[-1]],
                                 newNss=nsMapping) for term in lhs]
                body = len(body) == 1 and body[0] or And(body)
                head = [Uniterm(p,[s,o],newNss=nsMapping) for s,p,o in rhs]
                head = len(head) == 1 and head[0] or And(head)
                
                #first we identify body variables                        
                bodyVars = set(reduce(lambda x,y:x+y,
                                      [ list(extractVariables(i,existential=False)) 
                                                for i in iterCondition(body) ]))
                #then we identify head variables
                headVars = set(reduce(lambda x,y:x+y,
                                      [ list(extractVariables(i,existential=False)) 
                                                for i in iterCondition(head) ]))
                
                #then we identify those variables that should (or should not) be converted to skolem terms
                updateDict       = dict([(var,BNode()) for var in headVars if var not in bodyVars])
                
                for uniTerm in iterCondition(head):
                    newArg      = [ updateDict.get(i,i) for i in uniTerm.arg ]
                    uniTerm.arg = newArg
                                        
                exist=[list(extractVariables(i)) for i in breadth_first(head)]
                e=Exists(formula=head,
                         declare=set(reduce(lambda x,y:x+y,exist,[])))        
                if reduce(lambda x,y:x+y,exist):
                    head=e
                    assert e.declare,exist    
                
                self.formulae.append(Rule(Clause(body,head),declare=allVars))

    def __iter__(self):
        for f in self.formulae:
            yield f

class Rule(object):
    """
    RULE ::= 'Forall' Var* CLAUSE
    
    Example: {?C rdfs:subClassOf ?SC. ?M a ?C} => {?M a ?SC}.
    
    >>> clause = Clause(And([Uniterm(RDFS.subClassOf,[Variable('C'),Variable('SC')]),
    ...                      Uniterm(RDF.type,[Variable('M'),Variable('C')])]),
    ...                 Uniterm(RDF.type,[Variable('M'),Variable('SC')]))
    >>> Rule(clause,[Variable('M'),Variable('SC'),Variable('C')])
    Forall ?M ?SC ?C ( ?SC(?M) :- And( rdfs:subClassOf(?C ?SC) ?C(?M) ) )
    
    """
    def __init__(self,clause,declare=None,nsMapping=None,negativeStratus=False):
        self.negativeStratus=negativeStratus
        self.nsMapping = nsMapping and nsMapping or {}
        self.formula = clause
        self.declare = declare and declare or []

    def n3(self):
        """
        Render a rule as N3 (careful to use e:tuple (_: ?X) skolem functions for existentials in the head)

        >>> clause = Clause(And([Uniterm(RDFS.subClassOf,[Variable('C'),Variable('SC')]),
        ...                      Uniterm(RDF.type,[Variable('M'),Variable('C')])]),
        ...                 Uniterm(RDF.type,[Variable('M'),Variable('SC')]))        
        >>> Rule(clause,[Variable('M'),Variable('SC'),Variable('C')]).n3()
        u'{ ?C rdfs:subClassOf ?SC .\\n ?M a ?C } => { ?M a ?SC }'
                
        """
        return u'{ %s } => { %s }'%(self.formula.body.n3(),
                                    self.formula.head.n3())
#        "Forall %s ( %r )"%(' '.join([var.n3() for var in self.declare]),
#                               self.formula)

    def __eq__(self,other):
        return hash(self.formula)==hash(other.formula)
        
    def __hash__(self):
        """
        >>> a=Clause(And([Uniterm(RDFS.subClassOf,[Variable('C'),Variable('SC')]),
        ...             Uniterm(RDF.type,[Variable('M'),Variable('C')])]),
        ...        Uniterm(RDF.type,[Variable('M'),Variable('SC')]))
        >>> b=Clause(And([Uniterm(RDFS.subClassOf,[Variable('C'),Variable('SC')]),
        ...             Uniterm(RDF.type,[Variable('M'),Variable('C')])]),
        ...        Uniterm(RDF.type,[Variable('M'),Variable('SC')]))
        >>> d=set()
        >>> d.add(a)
        >>> b in d
        True
        >>> hash(a) == hash(b)
        True
        >>> EX_NS = Namespace('http://example.com/')
        >>> a=Clause(Uniterm(RDF.type,[Variable('C'),EX_NS.Foo]),
        ...          Uniterm(RDF.type,[Variable('C'),EX_NS.Bar]))
        >>> b=Clause(Uniterm(RDF.type,[Variable('C'),EX_NS.Bar]),
        ...          Uniterm(RDF.type,[Variable('C'),EX_NS.Foo]))
        >>> a == b
        False
        """
        return hash(self.formula)

    def __repr__(self):
        return "Forall %s ( %r )"%(' '.join([var.n3() for var in self.declare]),
                               self.formula)    
class Clause(object):
    """
    Facts are *not* modelled formally as rules with empty bodies
    
    Implies ::= ATOMIC ':-' CONDITION
    
    Use body / head instead of if/then (native language clash)
    
    Example: {?C rdfs:subClassOf ?SC. ?M a ?C} => {?M a ?SC}.
    
    >>> Clause(And([Uniterm(RDFS.subClassOf,[Variable('C'),Variable('SC')]),
    ...             Uniterm(RDF.type,[Variable('M'),Variable('C')])]),
    ...        Uniterm(RDF.type,[Variable('M'),Variable('SC')]))
    ?SC(?M) :- And( rdfs:subClassOf(?C ?SC) ?C(?M) )
    """
    def __init__(self,body,head):
        self.body = body
        self.head = head
        from FuXi.Rete.Network import HashablePatternList
        antHash=HashablePatternList(
                    [term.toRDFTuple() for term in body],skipBNodes=True)
        consHash=HashablePatternList(
                    [term.toRDFTuple() for term in head],skipBNodes=True)
        self._bodyHash = hash(antHash)
        self._headHash = hash(consHash)             
        self._hash     = hash((self._headHash,self._bodyHash))                                                      
        
    def __eq__(self,other):
        return hash(self)==hash(other)
        
    def __hash__(self):
        """
        >>> a=Clause(And([Uniterm(RDFS.subClassOf,[Variable('C'),Variable('SC')]),
        ...             Uniterm(RDF.type,[Variable('M'),Variable('C')])]),
        ...        Uniterm(RDF.type,[Variable('M'),Variable('SC')]))
        >>> b=Clause(And([Uniterm(RDFS.subClassOf,[Variable('C'),Variable('SC')]),
        ...             Uniterm(RDF.type,[Variable('M'),Variable('C')])]),
        ...        Uniterm(RDF.type,[Variable('M'),Variable('SC')]))
        >>> d=set()
        >>> d.add(a)
        >>> b in d
        True
        >>> hash(a) == hash(b)
        True
        
        >>> d={a:True}
        >>> b in d
        True
        """
        return self._hash
        
    def asTuple(self):
        return (self.body,self.head)
        
    def __repr__(self):
        if isinstance(self.body,SetOperator) and not len(self.body):
            return "%r :-"%self.head
        return "%r :- %r"%(self.head,self.body)
    
    def n3(self):
        return u'{ %s } => { %s }'%(self.body.n3(),self.head.n3())    
        
def test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    test()