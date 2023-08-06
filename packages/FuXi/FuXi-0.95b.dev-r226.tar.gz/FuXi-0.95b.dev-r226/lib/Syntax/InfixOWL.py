#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
RDFLib Python binding for OWL Abstract Syntax

see: http://www.w3.org/TR/owl-semantics/syntax.html
     http://owl-workshop.man.ac.uk/acceptedLong/submission_9.pdf

3.2.3 Axioms for complete classes without using owl:equivalentClass

  Named class description of type 2 (with owl:oneOf) or type 4-6 (with owl:intersectionOf, owl:unionOf or owl:complementOf
  
Uses Manchester Syntax for __repr__  

>>> exNs = Namespace('http://example.com/')        
>>> namespace_manager = NamespaceManager(Graph())
>>> namespace_manager.bind('ex', exNs, override=False)
>>> namespace_manager.bind('owl', OWL_NS, override=False)
>>> g = Graph()    
>>> g.namespace_manager = namespace_manager

Now we have an empty graph, we can construct OWL classes in it
using the Python classes defined in this module

>>> a = Class(exNs.Opera,graph=g)

Now we can assert rdfs:subClassOf and owl:equivalentClass relationships 
(in the underlying graph) with other classes using the 'subClassOf' 
and 'equivalentClass' descriptors which can be set to a list
of objects for the corresponding predicates.

>>> a.subClassOf = [exNs.MusicalWork]

We can then access the rdfs:subClassOf relationships

>>> print list(a.subClassOf)
[Class: ex:MusicalWork ]

This can also be used against already populated graphs:

#>>> owlGraph = Graph().parse(OWL_NS)
#>>> namespace_manager.bind('owl', OWL_NS, override=False)
#>>> owlGraph.namespace_manager = namespace_manager
#>>> list(Class(OWL_NS.Class,graph=owlGraph).subClassOf)
#[Class: rdfs:Class ]

Operators are also available.  For instance we can add ex:Opera to the extension
of the ex:CreativeWork class via the '+=' operator

>>> a
Class: ex:Opera SubClassOf: ex:MusicalWork
>>> b = Class(exNs.CreativeWork,graph=g)
>>> b += a
>>> print list(a.subClassOf)
[Class: ex:CreativeWork , Class: ex:MusicalWork ]

And we can then remove it from the extension as well

>>> b -= a
>>> a
Class: ex:Opera SubClassOf: ex:MusicalWork

Boolean class constructions can also  be created with Python operators
For example, The | operator can be used to construct a class consisting of a owl:unionOf 
the operands:

>>> c =  a | b | Class(exNs.Work,graph=g)
>>> c
( ex:Opera or ex:CreativeWork or ex:Work )

Boolean class expressions can also be operated as lists (using python list operators)

>>> del c[c.index(Class(exNs.Work,graph=g))]
>>> c
( ex:Opera or ex:CreativeWork )

The '&' operator can be used to construct class intersection:
      
>>> woman = Class(exNs.Female,graph=g) & Class(exNs.Human,graph=g)
>>> woman.identifier = exNs.Woman
>>> woman
( ex:Female and ex:Human )
>>> len(woman)
2

Enumerated classes can also be manipulated

>>> contList = [Class(exNs.Africa,graph=g),Class(exNs.NorthAmerica,graph=g)]
>>> EnumeratedClass(members=contList,graph=g)
{ ex:Africa ex:NorthAmerica }

owl:Restrictions can also be instanciated:

>>> Restriction(exNs.hasParent,graph=g,allValuesFrom=exNs.Human)
( ex:hasParent only ex:Human )

Restrictions can also be created using Manchester OWL syntax in 'colloquial' Python 
>>> exNs.hasParent |some| Class(exNs.Physician,graph=g)
( ex:hasParent some ex:Physician )

>>> Property(exNs.hasParent,graph=g) |max| Literal(1)
( ex:hasParent max 1 )

#>>> print g.serialize(format='pretty-xml')

"""
import os
from pprint import pprint
from rdflib import Namespace
from rdflib import plugin,RDF,RDFS,URIRef,BNode,Literal,Variable
from rdflib.Literal import _XSD_NS
from rdflib.Identifier import Identifier
from rdflib.util import first
from rdflib.store import Store
from rdflib.Graph import Graph
from rdflib.Collection import Collection
from rdflib.syntax.NamespaceManager import NamespaceManager

"""
From: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/384122

Python has the wonderful "in" operator and it would be nice to have additional 
infix operator like this. This recipe shows how (almost) arbitrary infix 
operators can be defined.

"""

# definition of an Infix operator class
# this recipe also works in jython
# calling sequence for the infix is either:
#  x |op| y
# or:
# x <<op>> y

class Infix:
    def __init__(self, function):
        self.function = function
    def __ror__(self, other):
        return Infix(lambda x, self=self, other=other: self.function(other, x))
    def __or__(self, other):
        return self.function(other)
    def __rlshift__(self, other):
        return Infix(lambda x, self=self, other=other: self.function(other, x))
    def __rshift__(self, other):
        return self.function(other)
    def __call__(self, value1, value2):
        return self.function(value1, value2)

OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")

nsBinds = {
    'skos': 'http://www.w3.org/2004/02/skos/core#',
    'rdf' : RDF.RDFNS,
    'rdfs': RDFS.RDFSNS,
    'owl' : OWL_NS,       
    'dc'  : "http://purl.org/dc/elements/1.1/",
}

def generateQName(graph,uri):
    prefix,uri,localName = graph.compute_qname(classOrIdentifier(uri)) 
    return u':'.join([prefix,localName])    

def classOrTerm(thing):
    if isinstance(thing,Class):
        return thing.identifier
    else:
        assert isinstance(thing,(URIRef,BNode,Literal))
        return thing

def classOrIdentifier(thing):
    if isinstance(thing,(Property,Class)):
        return thing.identifier
    else:
        assert isinstance(thing,(URIRef,BNode)),"Expecting a Class, Property, URIRef, or BNode.."
        return thing

def propertyOrIdentifier(thing):
    if isinstance(thing,Property):
        return thing.identifier
    else:
        assert isinstance(thing,URIRef)
        return thing

def manchesterSyntax(thing,store,boolean=None,transientList=False):
    """
    Core serialization
    """
    assert thing is not None
    if boolean:
        if transientList:
            liveChildren=iter(thing)
            children = [manchesterSyntax(child,store) for child in thing ]
        else:
            liveChildren=iter(Collection(store,thing))
            children = [manchesterSyntax(child,store) for child in Collection(store,thing)]
        if boolean == OWL_NS.intersectionOf:
            childList=[]
            named = []
            for child in liveChildren:
                if isinstance(child,URIRef):
                    named.append(child)
                else:
                    childList.append(child)
            if named:
                def castToQName(x):
                    prefix,uri,localName = store.compute_qname(x) 
                    return u':'.join([prefix,localName])
                
                if len(named) > 1:
                    prefix = '( '+ ' and '.join(map(castToQName,named)) + ' )'                
                else:
                    prefix = manchesterSyntax(named[0],store)
                if childList:
                    return prefix+ ' that '+' and '.join(
                             map(lambda x:manchesterSyntax(x,store),childList))
                else:
                    return prefix
            else:
                return '( '+ ' and '.join(children) + ' )'
        elif boolean == OWL_NS.unionOf:
            return '( '+ ' or '.join(children) + ' )'
        elif boolean == OWL_NS.oneOf:
            return '{ '+ ' '.join(children) +' }'
        else:            
            assert boolean == OWL_NS.complementOf
    elif OWL_NS.Restriction in store.objects(subject=thing, predicate=RDF.type):
        prop = list(store.objects(subject=thing, predicate=OWL_NS.onProperty))[0]
        prefix,uri,localName = store.compute_qname(prop)
        propString = u':'.join([prefix,localName])
        for onlyClass in store.objects(subject=thing, predicate=OWL_NS.allValuesFrom):
            return '( %s only %s )'%(propString,manchesterSyntax(onlyClass,store))
        for someClass in store.objects(subject=thing, predicate=OWL_NS.someValuesFrom):    
            return '( %s some %s )'%(propString,manchesterSyntax(someClass,store))
        cardLookup = {OWL_NS.maxCardinality:'max',OWL_NS.minCardinality:'min',OWL_NS.cardinality:'equals'}
        for s,p,o in store.triples_choices((thing,cardLookup.keys(),None)):            
            return '( %s %s %s )'%(propString,cardLookup[p],o.encode('utf-8'))
    compl = list(store.objects(subject=thing, predicate=OWL_NS.complementOf)) 
    if compl:
        return '( not %s )'%(manchesterSyntax(compl[0],store))
    else:
        for boolProp,col in store.query("SELECT ?p ?bool WHERE { ?class a owl:Class; ?p ?bool . ?bool rdf:first ?foo }",
                                         initBindings={Variable("?class"):thing},
                                         initNs=nsBinds):
            if not isinstance(thing,URIRef):                
                return manchesterSyntax(col,store,boolean=boolProp)
        try:
            prefix,uri,localName = store.compute_qname(thing) 
            qname = u':'.join([prefix,localName])
        except Exception,e:
            if isinstance(thing,BNode):
                return thing.n3()
            return "<"+thing+">"
            print list(store.objects(subject=thing,predicate=RDF.type))
            raise
            return '[]'#+thing._id.encode('utf-8')+'</em>'            
        if (thing,RDF.type,OWL_NS.Class) not in store:
            return qname.encode('utf-8')
        else:
            return qname.encode('utf-8')

def GetIdentifiedClasses(graph):
    for c in graph.subjects(predicate=RDF.type,object=OWL_NS.Class):
        if isinstance(c,URIRef):
            yield Class(c)

class Individual(object):
    """
    A typed individual
    """
    factoryGraph = Graph()
    def __init__(self, identifier=None,graph=None):
        self.__identifier = identifier is not None and identifier or BNode()
        if graph is None:
            self.graph = self.factoryGraph
        else:
            self.graph = graph    
        self.qname = None
        if not isinstance(self.identifier,BNode):
            try:
                prefix,uri,localName = self.graph.compute_qname(self.identifier) 
                self.qname = u':'.join([prefix,localName])
            except:
                pass
    
    def _get_type(self):
        for _t in self.graph.objects(subject=self.identifier,predicate=RDF.type):
            yield _t
    def _set_type(self, kind):
        if not kind:
            return  
        if isinstance(kind,(Individual,Identifier)):
            self.graph.add((self.identifier,RDF.type,classOrIdentifier(kind)))
        else:
            for c in kind:
                assert isinstance(c,(Individual,Identifier))
                self.graph.add((self.identifier,RDF.type,classOrIdentifier(c)))
    type = property(_get_type, _set_type)

    def _get_identifier(self):
        return self.__identifier
    def _set_identifier(self, i):
        assert i
        if i != self.__identifier:
            oldStmtsOut = [(p,o) for s,p,o in self.graph.triples((self.__identifier,None,None))]
            oldStmtsIn  = [(s,p) for s,p,o in self.graph.triples((None,None,self.__identifier))]
            for p1,o1 in oldStmtsOut:                
                self.graph.remove((self.__identifier,p1,o1))
            for s1,p1 in oldStmtsIn:                
                self.graph.remove((s1,p1,self.__identifier))
            self.__identifier = i
            self.graph.addN([(i,p1,o1,self.graph) for p1,o1 in oldStmtsOut])
            self.graph.addN([(s1,p1,i,self.graph) for s1,p1 in oldStmtsIn])
    identifier = property(_get_identifier, _set_identifier)

class AnnotatibleTerms(Individual):
    """
    Terms in an OWL ontology with rdfs:label and rdfs:comment
    """
    def __init__(self,identifier,graph):
        super(AnnotatibleTerms, self).__init__(identifier,graph)
    def _get_comment(self):
        for comment in self.graph.objects(subject=self.identifier,predicate=RDFS.comment):
            yield comment
    def _set_comment(self, comment):
        if not comment:
            return        
        if isinstance(comment,Identifier):
            self.graph.add((self.identifier,RDFS.comment,comment))
        else:
            for c in comment:
                self.graph.add((self.identifier,RDFS.comment,c))
    comment = property(_get_comment, _set_comment)

    def _get_seeAlso(self):
        for sA in self.graph.objects(subject=self.identifier,predicate=RDFS.seeAlso):
            yield sA
    def _set_seeAlso(self, seeAlsos):
        if not seeAlsos:
            return        
        for s in seeAlsos:
            self.graph.add((self.identifier,RDFS.seeAlso,s))
    seeAlso = property(_get_seeAlso, _set_seeAlso)

    def _get_label(self):
        for label in self.graph.objects(subject=self.identifier,predicate=RDFS.label):
            yield label
    def _set_label(self, label):
        if not label:
            return        
        if isinstance(label,Identifier):
            self.graph.add((self.identifier,RDFS.label,label))
        else:
            for l in label:
                self.graph.add((self.identifier,RDFS.label,l))
    label = property(_get_label, _set_label)

class Ontology(AnnotatibleTerms):
    """ The owl ontology metadata"""
    def __init__(self, identifier=None,imports=None,comment=None,graph=None):
        super(Ontology, self).__init__(identifier,graph)
        self.imports = imports and imports or []
        self.comment = imports and imports or []
        if (self.identifier,RDF.type,OWL_NS.Ontology) not in self.graph:
            self.graph.add((self.identifier,RDF.type,OWL_NS.Ontology))

    def setVersion(self,version):
        self.graph.set((self.identifier,OWL_NS.versionInfo,version))

    def _get_imports(self):
        for owl in self.graph.objects(subject=self.identifier,predicate=OWL_NS['imports']):
            yield owl
    def _set_imports(self, other):
        if not other:
            return        
        for o in other:
            self.graph.add((self.identifier,OWL_NS['imports'],o))
    imports = property(_get_imports, _set_imports)

def AllClasses(graph):
    prevClasses=set()
    for c in graph.subjects(predicate=RDF.type,object=OWL_NS.Class):
        if c not in prevClasses:
            prevClasses.add(c)
            yield Class(c)            

def AllProperties(graph):
    prevProps=set()
    for s,p,o in graph.triples_choices(
               (None,RDF.type,[OWL_NS.Symmetric,
                               OWL_NS.FunctionalProperty,
                               OWL_NS.InverseFunctionalProperty,
                               OWL_NS.TransitiveProperty,
                               OWL_NS.DatatypeProperty,
                               OWL_NS.ObjectProperty])):
        if o in [OWL_NS.Symmetric,
                 OWL_NS.InverseFunctionalProperty,
                 OWL_NS.TransitiveProperty,
                 OWL_NS.ObjectProperty]:
            bType=OWL_NS.ObjectProperty
        else:
            bType=OWL_NS.DatatypeProperty
        if s not in prevProps:
            prevProps.add(s)
            yield Property(s,
                           graph=graph,
                           baseType=bType)            
    
def CastClass(c,graph=None):
    graph = graph is None and c.factoryGraph or graph
    for kind in graph.objects(subject=classOrIdentifier(c),
                              predicate=RDF.type):
        if kind == OWL_NS.Restriction:
            prop = list(graph.objects(subject=classOrIdentifier(c),
                                     predicate=OWL_NS.onProperty))[0]
            return Restriction(prop, graph,identifier=classOrIdentifier(c))
        else:
            for s,p,o in graph.triples_choices((classOrIdentifier(c),
                                                [OWL_NS.intersectionOf,
                                                 OWL_NS.unionOf,
                                                 OWL_NS.oneOf],
                                                None)):
                if p == OWL_NS.oneOf:
                    return EnumeratedClass(classOrIdentifier(c),graph=graph)
                else:
                    return BooleanClass(classOrIdentifier(c),operator=p,graph=graph)
            #assert (classOrIdentifier(c),RDF.type,OWL_NS.Class) in graph
            return Class(classOrIdentifier(c),graph=graph,skipOWLClassMembership=True)
    
class Class(AnnotatibleTerms):
    """
    'General form' for classes:
    
    The Manchester Syntax (supported in Protege) is used as the basis for the form 
    of this class
    
    See: http://owl-workshop.man.ac.uk/acceptedLong/submission_9.pdf:
    
    ‘Class:’ classID {Annotation
                  ( (‘SubClassOf:’ ClassExpression)
                  | (‘EquivalentTo’ ClassExpression)
                  | (’DisjointWith’ ClassExpression)) }
    
    Appropriate excerpts from OWL Reference:
    
    ".. Subclass axioms provide us with partial definitions: they represent 
     necessary but not sufficient conditions for establishing class 
     membership of an individual."
     
   ".. A class axiom may contain (multiple) owl:equivalentClass statements"   
                  
    "..A class axiom may also contain (multiple) owl:disjointWith statements.."
    
    "..An owl:complementOf property links a class to precisely one class 
      description."
      
    """
    def __init__(self, identifier=None,subClassOf=None,equivalentClass=None,
                       disjointWith=None,complementOf=None,graph=None,
                       skipOWLClassMembership = False,comment=None):
        super(Class, self).__init__(identifier,graph)
        if not skipOWLClassMembership and (self.identifier,RDF.type,OWL_NS.Class) not in self.graph:
            self.graph.add((self.identifier,RDF.type,OWL_NS.Class))
        
        self.subClassOf      = subClassOf and subClassOf or [] 
        self.equivalentClass = equivalentClass and equivalentClass or []
        self.disjointWith    = disjointWith  and disjointWith or []
        if complementOf:
            self.complementOf    = complementOf
        self.comment = comment and comment or []
    
    def __iadd__(self, other):
        assert isinstance(other,Class)
        other.subClassOf = [self]
        return self

    def __isub__(self, other):
        assert isinstance(other,Class)
        self.graph.remove((classOrIdentifier(other),RDFS.subClassOf,self.identifier))
        return self
    
    def __invert__(self):
        """
        Shorthand for Manchester syntax's not operator
        """
        return Class(complementOf=self)

    def __or__(self,other):
        """
        Construct an anonymous class description consisting of the union of this class and '
        other' and return it
        """
        return BooleanClass(operator=OWL_NS.unionOf,members=[self,other],graph=self.graph)

    def __and__(self,other):
        """
        Construct an anonymous class description consisting of the intersection of this class and '
        other' and return it
        """
        return BooleanClass(operator=OWL_NS.intersectionOf,members=[self,other],graph=self.graph)
            
    def _get_subClassOf(self):
        for anc in self.graph.objects(subject=self.identifier,predicate=RDFS.subClassOf):
            yield Class(anc,graph=self.graph)
    def _set_subClassOf(self, other):
        if not other:
            return        
        for sc in other:
            self.graph.add((self.identifier,RDFS.subClassOf,classOrIdentifier(sc)))
    subClassOf = property(_get_subClassOf, _set_subClassOf)

    def _get_equivalentClass(self):
        for ec in self.graph.objects(subject=self.identifier,predicate=OWL_NS.equivalentClass):
            yield Class(ec,graph=self.graph)
    def _set_equivalentClass(self, other):
        if not other:
            return
        for sc in other:
            self.graph.add((self.identifier,OWL_NS.equivalentClass,classOrIdentifier(sc)))
    equivalentClass = property(_get_equivalentClass, _set_equivalentClass)

    def _get_disjointWith(self):
        for dc in self.graph.objects(subject=self.identifier,predicate=OWL_NS.disjointWith):
            yield Class(dc,graph=self.graph)
    def _set_disjointWith(self, other):
        if not other:
            return
        for c in other:
            self.graph.add((self.identifier,OWL_NS.disjointWith,classOrIdentifier(c)))
    disjointWith = property(_get_disjointWith, _set_disjointWith)

    def _get_complementOf(self):
        comp = list(self.graph.objects(subject=self.identifier,predicate=OWL_NS.complementOf))
        if not comp:
            return None
        elif len(comp) == 1:
            return Class(comp[0],graph=self.graph)
        else:
            raise Exception(len(comp))
        
    def _set_complementOf(self, other):
        if not other:
            return
        self.graph.add((self.identifier,OWL_NS.complementOf,classOrIdentifier(other)))
    complementOf = property(_get_complementOf, _set_complementOf)

    def _get_seeAlso(self):
        for ec in self.graph.objects(subject=self.identifier,predicate=RDFS.seeAlso):
            yield Class(ec,graph=self.graph)
                
    def _set_seeAlso(self, others):
        if not others:
            return
        for link in others:
            self.graph.add((self.identifier,RDFS.seeAlso,link))
    seeAlso = property(_get_seeAlso, _set_seeAlso)
    
    def isPrimitive(self):
        if (self.identifier,RDF.type,OWL_NS.Restriction) in self.graph:
            return False
        sc = list(self.subClassOf)
        ec = list(self.equivalentClass)
        for boolClass,p,rdfList in self.graph.triples_choices((self.identifier,
                                                               [OWL_NS.intersectionOf,
                                                                OWL_NS.unionOf],
                                                                None)):
            ec.append(manchesterSyntax(rdfList,self.graph,boolean=p))
        for e in ec:
            return False
        if self.complementOf:
            return False
        return True
    
    def subSumpteeIds(self):
        for s in self.graph.subjects(predicate=RDFS.subClassOf,object=self.identifier):
            yield s
    
    def __repr__(self,full=False,normalization=True):
        """
        Returns the Manchester Syntax equivalent for this class
        """
        exprs = []
        sc = list(self.subClassOf)
        ec = list(self.equivalentClass)
        for boolClass,p,rdfList in self.graph.triples_choices((self.identifier,
                                                               [OWL_NS.intersectionOf,
                                                                OWL_NS.unionOf],
                                                                None)):
            ec.append(manchesterSyntax(rdfList,self.graph,boolean=p))
        dc = list(self.disjointWith)
        c  = self.complementOf
        klassKind = ''
        label = list(self.graph.objects(self.identifier,RDFS.label))
        label = label and '('+label[0]+')' or ''
        if sc:
            if full:
                scJoin = '\n                '
            else:
                scJoin = ', '
            necStatements = [
              isinstance(s,Class) and isinstance(self.identifier,BNode) and
                                      repr(CastClass(s,self.graph)) or
                                      #repr(BooleanClass(classOrIdentifier(s),
                                      #                  operator=None,
                                      #                  graph=self.graph)) or 
              manchesterSyntax(classOrIdentifier(s),self.graph) for s in sc]
            if necStatements:
                klassKind = "Primitive Type %s"%label
            exprs.append("SubClassOf: %s"%scJoin.join(necStatements))
            if full:
                exprs[-1]="\n    "+exprs[-1]
        if ec:
            nec_SuffStatements = [    
              isinstance(s,basestring) and s or 
              manchesterSyntax(classOrIdentifier(s),self.graph) for s in ec]
            if nec_SuffStatements:
                klassKind = "A Defined Class %s"%label
            exprs.append("EquivalentTo: %s"%', '.join(nec_SuffStatements))
            if full:
                exprs[-1]="\n    "+exprs[-1]
        if dc:
            if c:
                dc.append(c)
            exprs.append("DisjointWith %s\n"%'\n                 '.join([
              manchesterSyntax(classOrIdentifier(s),self.graph) for s in dc]))
            if full:
                exprs[-1]="\n    "+exprs[-1]
        descr = list(self.graph.objects(self.identifier,RDFS.comment))
        if full and normalization:
            klassDescr = klassKind and '\n    ## %s ##'%klassKind +\
            (descr and "\n    %s"%descr[0] or '') + ' . '.join(exprs) or ' . '.join(exprs)
        else:
            klassDescr = full and (descr and "\n    %s"%descr[0] or '') or '' + ' . '.join(exprs)
        return (isinstance(self.identifier,BNode) and "Some Class " or "Class: %s "%self.qname)+klassDescr

class OWLRDFListProxy(object):
    def __init__(self,rdfList,members=None,graph=Graph()):
        members = members and members or []
        if rdfList:
            self._rdfList = Collection(graph,rdfList[0])
            for member in members:
                if member not in self._rdfList:
                    self._rdfList.append(classOrIdentifier(member))
        else:
            self._rdfList = Collection(self.graph,BNode(),
                                       [classOrIdentifier(m) for m in members])
            self.graph.add((self.identifier,self._operator,self._rdfList.uri)) 

    #Redirect python list accessors to the underlying Collection instance
    def __len__(self):
        return len(self._rdfList)

    def index(self, item):
        return self._rdfList.index(classOrIdentifier(item))
    
    def __getitem__(self, key):
        return self._rdfList[key]

    def __setitem__(self, key, value):
        self._rdfList[key] = classOrIdentifier(value)
        
    def __delitem__(self, key):
        del self._rdfList[key]    
        
    def clear(self):
        self._rdfList.clear()    

    def __iter__(self):
        for item in self._rdfList:
            yield item

    def __contains__(self, item):
        for i in self._rdfList:
            if i == classOrIdentifier(item):
                return 1
        return 0

    def __iadd__(self, other):
        self._rdfList.append(classOrIdentifier(other))

class EnumeratedClass(Class,OWLRDFListProxy):
    """
    Class for owl:oneOf forms:
    
    OWL Abstract Syntax is used
    
    axiom ::= 'EnumeratedClass(' classID ['Deprecated'] { annotation } { individualID } ')'    
    """
    _operator = OWL_NS.oneOf
    def isPrimitive(self):
        return False
    def __init__(self, identifier=None,members=None,graph=None):
        Class.__init__(self,identifier,graph = graph)
        members = members and members or []
        rdfList = list(self.graph.objects(predicate=OWL_NS.oneOf,subject=self.identifier))
        OWLRDFListProxy.__init__(self, rdfList, members, graph = graph)
    def __repr__(self):
        """
        Returns the Manchester Syntax equivalent for this class
        """
        return manchesterSyntax(self._rdfList.uri,self.graph,boolean=self._operator)        

BooleanPredicates = [OWL_NS.intersectionOf,OWL_NS.unionOf]

class BooleanClass(Class,OWLRDFListProxy):
    """
    See: http://www.w3.org/TR/owl-ref/#Boolean
    
    owl:complementOf is an attribute of Class, however
    
    """
    def __init__(self,identifier=None,operator=OWL_NS.intersectionOf,
                 members=None,graph=None):
        if operator is None:
            props=[]
            for s,p,o in graph.triples_choices((identifier,
                                                [OWL_NS.intersectionOf,
                                                 OWL_NS.unionOf],
                                                 None)):
                props.append(p)
                operator = p
            assert len(props)==1,repr(props)
        Class.__init__(self,identifier,graph = graph)
        assert operator in [OWL_NS.intersectionOf,OWL_NS.unionOf], str(operator)
        self._operator = operator
        rdfList = list(self.graph.objects(predicate=operator,subject=self.identifier))
        assert not members or not rdfList,"This is a previous boolean class description!"+repr(Collection(self.graph,rdfList[0]).n3())        
        OWLRDFListProxy.__init__(self, rdfList, members, graph = graph)

    def isPrimitive(self):
        return False

    def changeOperator(self,newOperator):
        """
        Converts a unionOf / intersectionOf class expression into one 
        that instead uses the given operator
        
        
        >>> testGraph = Graph()
        >>> Individual.factoryGraph = testGraph
        >>> EX = Namespace("http://example.com/")
        >>> namespace_manager = NamespaceManager(Graph())
        >>> namespace_manager.bind('ex', EX, override=False)
        >>> testGraph.namespace_manager = namespace_manager
        >>> fire  = Class(EX.Fire)
        >>> water = Class(EX.Water) 
        >>> testClass = BooleanClass(members=[fire,water])
        >>> testClass
        ( ex:Fire and ex:Water )
        >>> testClass.changeOperator(OWL_NS.unionOf)
        >>> testClass
        ( ex:Fire or ex:Water )
        >>> try: testClass.changeOperator(OWL_NS.unionOf)
        ... except Exception, e: print e
        The new operator is already being used!
        
        """
        assert newOperator != self._operator,"The new operator is already being used!"
        self.graph.remove((self.identifier,self._operator,self._rdfList.uri))
        self.graph.add((self.identifier,newOperator,self._rdfList.uri))
        self._operator = newOperator

    def __repr__(self):
        """
        Returns the Manchester Syntax equivalent for this class
        """
        return manchesterSyntax(self._rdfList.uri,self.graph,boolean=self._operator)

    def __or__(self,other):
        """
        Adds other to the list and returns self
        """
        assert self._operator == OWL_NS.unionOf
        self._rdfList.append(classOrIdentifier(other))
        return self

def AllDifferent(members):
    """
    DisjointClasses(' description description { description } ')'
    
    """
    pass

class Restriction(Class):
    """
    restriction ::= 'restriction(' datavaluedPropertyID dataRestrictionComponent 
                                 { dataRestrictionComponent } ')'
                  | 'restriction(' individualvaluedPropertyID 
                      individualRestrictionComponent 
                      { individualRestrictionComponent } ')'    
    """
    
    restrictionKinds = [OWL_NS.allValuesFrom,
                        OWL_NS.someValuesFrom,
                        OWL_NS.hasValue,
                        OWL_NS.maxCardinality,
                        OWL_NS.minCardinality]
    
    def __init__(self,onProperty,graph = Graph(),allValuesFrom=None,someValuesFrom=None,value=None,
                      cardinality=None,maxCardinality=None,minCardinality=None,identifier=None):
        super(Restriction, self).__init__(identifier,
                                          graph=graph,
                                          skipOWLClassMembership=True)
        if (self.identifier,OWL_NS.onProperty,propertyOrIdentifier(onProperty)) not in graph:
            graph.add((self.identifier,OWL_NS.onProperty,propertyOrIdentifier(onProperty)))
        self.onProperty = onProperty
        restrTypes = [
                      (allValuesFrom,OWL_NS.allValuesFrom ),
                      (someValuesFrom,OWL_NS.someValuesFrom),
                      (value,OWL_NS.hasValue),
                      (cardinality,OWL_NS.cardinality),
                      (maxCardinality,OWL_NS.maxCardinality),
                      (minCardinality,OWL_NS.minCardinality)]
        validRestrProps = [(i,oTerm) for (i,oTerm) in restrTypes if i] 
        assert len(validRestrProps) < 2
        for val,oTerm in validRestrProps:
            self.graph.add((self.identifier,oTerm,classOrTerm(val)))   
        if (self.identifier,RDF.type,OWL_NS.Restriction) not in self.graph:
            self.graph.add((self.identifier,RDF.type,OWL_NS.Restriction))

    def isPrimitive(self):
        return False

    def _get_onProperty(self):
        return list(self.graph.objects(subject=self.identifier,predicate=OWL_NS.onProperty))[0]
    def _set_onProperty(self, prop):
        triple = (self.identifier,OWL_NS.onProperty,propertyOrIdentifier(prop))
        if not prop:
            return
        elif triple in self.graph:
            return
        else:
            self.graph.set(triple)
    onProperty = property(_get_onProperty, _set_onProperty)

    def _get_allValuesFrom(self):
        for i in self.graph.objects(subject=self.identifier,predicate=OWL_NS.allValuesFrom):
            return Class(i,graph=self.graph)
        return None
    def _set_allValuesFrom(self, other):
        triple = (self.identifier,OWL_NS.allValuesFrom,classOrIdentifier(other))
        if not other:
            return
        elif triple in self.graph:
            return
        else:
            self.graph.set(triple)
    allValuesFrom = property(_get_allValuesFrom, _set_allValuesFrom)

    def _get_someValuesFrom(self):
        for i in self.graph.objects(subject=self.identifier,predicate=OWL_NS.someValuesFrom):
            return Class(i,graph=self.graph)
        return None
    def _set_someValuesFrom(self, other):
        triple = (self.identifier,OWL_NS.someValuesFrom,classOrIdentifier(other))
        if not other:
            return
        elif triple in self.graph:
            return
        else:
            self.graph.set(triple)
    someValuesFrom = property(_get_someValuesFrom, _set_someValuesFrom)

    def _get_hasValue(self):
        for i in self.graph.objects(subject=self.identifier,predicate=OWL_NS.hasValue):
            return Class(i,graph=self.graph)
        return None
    def _set_hasValue(self, other):
        triple = (self.identifier,OWL_NS.hasValue,classOrIdentifier(other))
        if not other:
            return
        elif triple in self.graph:
            return
        else:
            self.graph.set(triple)
    hasValue = property(_get_hasValue, _set_hasValue)

    def _get_cardinality(self):
        for i in self.graph.objects(subject=self.identifier,predicate=OWL_NS.cardinality):
            return Class(i,graph=self.graph)
        return None
    def _set_cardinality(self, other):
        triple = (self.identifier,OWL_NS.cardinality,classOrIdentifier(other))
        if not other:
            return
        elif triple in self.graph:
            return
        else:
            self.graph.set(triple)
    cardinality = property(_get_cardinality, _set_cardinality)

    def _get_maxCardinality(self):
        for i in self.graph.objects(subject=self.identifier,predicate=OWL_NS.maxCardinality):
            return Class(i,graph=self.graph)
        return None
    def _set_maxCardinality(self, other):
        triple = (self.identifier,OWL_NS.maxCardinality,classOrIdentifier(other))
        if not other:
            return
        elif triple in self.graph:
            return
        else:
            self.graph.set(triple)
    maxCardinality = property(_get_maxCardinality, _set_maxCardinality)

    def _get_minCardinality(self):
        for i in self.graph.objects(subject=self.identifier,predicate=OWL_NS.minCardinality):
            return Class(i,graph=self.graph)
        return None
    def _set_minCardinality(self, other):
        triple = (self.identifier,OWL_NS.minCardinality,classOrIdentifier(other))
        if not other:
            return
        elif triple in self.graph:
            return
        else:
            self.graph.set(triple)
    minCardinality = property(_get_minCardinality, _set_minCardinality)

    def restrictionKind(self):
        for p in self.graph.triple_choices((self.identifier,
                                            self.restrictionKinds,
                                            None)):
            return p.split(OWL_NS)[-1]
        raise
            
    def __repr__(self):
        """
        Returns the Manchester Syntax equivalent for this restriction
        """
        return manchesterSyntax(self.identifier,self.graph)

### Infix Operators ###

some     = Infix(lambda prop,_class: Restriction(prop,graph=_class.graph,someValuesFrom=_class))
only     = Infix(lambda prop,_class: Restriction(prop,graph=_class.graph,allValuesFrom=_class))
max      = Infix(lambda prop,_class: Restriction(prop,graph=prop.graph,maxCardinality=_class))
min      = Infix(lambda prop,_class: Restriction(prop,graph=prop.graph,minCardinality=_class))
exactly  = Infix(lambda prop,_class: Restriction(prop,graph=prop.graph,cardinality=_class))
value    = Infix(lambda prop,_class: Restriction(prop,graph=prop.graph,value=_class))

PropertyAbstractSyntax=\
"""
%s( %s { %s } 
%s
{ 'super(' datavaluedPropertyID ')'} ['Functional']
{ domain( %s ) } { range( %s ) } )"""

class Property(AnnotatibleTerms):
    """
    axiom ::= 'DatatypeProperty(' datavaluedPropertyID ['Deprecated'] { annotation } 
                { 'super(' datavaluedPropertyID ')'} ['Functional']
                { 'domain(' description ')' } { 'range(' dataRange ')' } ')'
            | 'ObjectProperty(' individualvaluedPropertyID ['Deprecated'] { annotation } 
                { 'super(' individualvaluedPropertyID ')' }
                [ 'inverseOf(' individualvaluedPropertyID ')' ] [ 'Symmetric' ] 
                [ 'Functional' | 'InverseFunctional' | 'Functional' 'InverseFunctional' |
                  'Transitive' ]
                { 'domain(' description ')' } { 'range(' description ')' } ')    
    """
    def __init__(self,identifier=None,graph = None,baseType=OWL_NS.ObjectProperty,
                      subPropertyOf=None,domain=None,range=None,inverseOf=None,
                      otherType=None,equivalentProperty=None,comment=None):
        super(Property, self).__init__(identifier,graph)
        assert not isinstance(self.identifier,BNode)
        if (self.identifier,RDF.type,baseType) not in self.graph:
            self.graph.add((self.identifier,RDF.type,baseType))
        self._baseType=baseType
        self.subPropertyOf = subPropertyOf
        self.inverseOf     = inverseOf
        self.domain        = domain
        self.range         = range
        self.comment = comment and comment or []

    def __repr__(self):
        rt=[]
        if OWL_NS.ObjectProperty in self.type:
            rt.append('ObjectProperty( %s annotation(%s)'\
                       %(self.qname,first(self.comment) and first(self.comment) or ''))
            if first(self.inverseOf):
                rt.append("  inverseOf( %s )%s"%(first(self.inverseOf),
                            OWL_NS.Symmetric in self.type and ' Symmetric' or ''))
            for s,p,roleType in self.graph.triples_choices((self.identifier,
                                                            RDF.type,
                                                            [OWL_NS.Functional,
                                                             OWL_NS.InverseFunctionalProperty,
                                                             OWL_NS.Transitive])):
                rt.append(roleType.split(OWL_NS)[-1])
        else:
            rt.append('DatatypeProperty( %s %s'\
                       %(self.qname,first(self.comment) and first(self.comment) or ''))            
            for s,p,roleType in self.graph.triples((self.identifier,
                                                    RDF.type,
                                                    OWL_NS.Functional)):
                rt.append('   Functional')
        def canonicalName(term,g):
            normalizedName=classOrIdentifier(term)
            if isinstance(normalizedName,BNode):
                return term
            elif normalizedName.startswith(_XSD_NS):
                return term
            elif first(g.triples_choices((
                      normalizedName,
                      [OWL_NS.unionOf,
                       OWL_NS.intersectionOf],None))):
                return repr(term)
            else:
                return str(term.qname)
        rt.append(' '.join(["   super( %s )"%canonicalName(superP,self.graph) 
                              for superP in self.subPropertyOf]))                        
        rt.append(' '.join(["   domain( %s )"% canonicalName(domain,self.graph) 
                              for domain in self.domain]))
        rt.append(' '.join(["   range( %s )"%canonicalName(range,self.graph) 
                              for range in self.range]))
        rt='\n'.join([expr for expr in rt if expr])
        rt+='\n)'
        return rt
                    
    def _get_subPropertyOf(self):
        for anc in self.graph.objects(subject=self.identifier,predicate=RDFS.subPropertyOf):
            yield Property(anc,graph=self.graph)
    def _set_subPropertyOf(self, other):
        if not other:
            return        
        for sP in other:
            self.graph.add((self.identifier,RDFS.subPropertyOf,classOrIdentifier(sP)))
    subPropertyOf = property(_get_subPropertyOf, _set_subPropertyOf)

    def _get_inverseOf(self):
        for anc in self.graph.objects(subject=self.identifier,predicate=OWL_NS.inverseOf):
            yield Property(anc,graph=self.graph)
    def _set_inverseOf(self, other):
        if not other:
            return        
        self.graph.add((self.identifier,OWL_NS.inverseOf,classOrIdentifier(other)))
    inverseOf = property(_get_inverseOf, _set_inverseOf)

    def _get_domain(self):
        for dom in self.graph.objects(subject=self.identifier,predicate=RDFS.domain):
            yield Class(dom,graph=self.graph)
    def _set_domain(self, other):
        if not other:
            return
        if isinstance(other,(Individual,Identifier)):
            self.graph.add((self.identifier,RDFS.domain,classOrIdentifier(other)))
        else:
            for dom in other:
                self.graph.add((self.identifier,RDFS.domain,classOrIdentifier(dom)))
    domain = property(_get_domain, _set_domain)

    def _get_range(self):
        for ran in self.graph.objects(subject=self.identifier,predicate=RDFS.range):
            yield Class(ran,graph=self.graph)
    def _set_range(self, ranges):
        if not ranges:
            return
        if isinstance(ranges,(Individual,Identifier)):
            self.graph.add((self.identifier,RDFS.range,classOrIdentifier(ranges)))
        else:        
            for range in ranges:
                self.graph.add((self.identifier,RDFS.range,classOrIdentifier(range)))
    range = property(_get_range, _set_range)
        
def test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    test()
