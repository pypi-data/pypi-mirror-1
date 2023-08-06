#!/usr/bin/env python
"""
rdf.py - Trio RDF Concepts
Copyright 2007, Sean B. Palmer, inamidst.com
Licensed under the Eiffel Forum License 2.

Package: http://inamidst.com/sw/trio/
"""

import operator, itertools, unicodedata

def error(msg): 
   import sys
   print >> sys.stderr, msg
   sys.exit(1)

class Message(unicode): 
   def __new__(cls, name): 
      msg = 'Import Error: Missing %s.py from %s'
      uri = 'http://inamidst.com/sw/trio/'
      return unicode.__new__(cls, msg % (name, uri))

   __getattr__ = lambda self, *args: error(self)
   __setattr__ = lambda self, *args: error(self)

def optional(name): 
   # @@ make this give better error messages
   try: exec 'import ' + name
   except ImportError: 
      return Message(name)
   return eval(name)

try: from __init__ import capabilities
except ImportError: 
   capabilities = False

if capabilities is False: 
   capabilities = ['grddl', 'notation3', 'ntriples', 'rdfxml', 
     'serialise', 'srx', 'turtle', 'web']

for name in capabilities: 
   o = optional(name)
   exec name + ' = o'
del o

class Triple(object): 
   counter = itertools.count(1)

   def __init__(self, subject, predicate, object): 
      self.subject = subject
      self.predicate = predicate
      self.object = object

      assert isinstance(subject, Term)
      assert isinstance(predicate, Term)
      assert isinstance(object, Term)

      self.ID = Triple.counter.next()

   def __hash__(self): 
      return hash(self.subject) ^ hash(self.predicate) \
             ^ hash(self.object) ^ 0x31337

   def __eq__(self, other): 
      if not isinstance(other, Triple): 
         return False
      return ((self.subject == other.subject) and 
              (self.predicate == other.predicate) and 
              (self.object == other.object))

   def __ne__(self, other): 
      return (not self.__eq__(other))

   def __repr__(self): 
      s, p, o = self.subject, self.predicate, self.object
      return 'Triple(%r, %r, %r)' % (s, p, o)
# t = Triple

class Store(object): 
   def __init__(self): 
      # These map terms to a set of triple IDs
      self.subjects = {}
      self.predicates = {}
      self.objects = {}

      # This maps triple IDs to triples
      self.triples = {}

   def add(self, triple): 
      # Check for duplicates
      if isinstance(triple.subject, Constant) or \
         isinstance(triple.predicate, Constant) or \
         isinstance(triple.predicate, Constant): 
         for t in self.get(triple.subject, triple.predicate, triple.object): 
            return False

      self.subjects.setdefault(triple.subject, set()).add(triple.ID)
      self.predicates.setdefault(triple.predicate, set()).add(triple.ID)
      self.objects.setdefault(triple.object, set()).add(triple.ID)

      self.triples[triple.ID] = triple
      return True

   def get(self, subject=None, predicate=None, object=None): 
      if not (subject or predicate or object): 
         for triple in self.triples.itervalues(): 
            yield triple
         return

      sets = (db.get(term) or set() for (db, term) in 
              ((self.subjects, subject), 
               (self.predicates, predicate), 
               (self.objects, object)) if term)
      for tID in reduce(operator.__and__, sets): 
         yield self.triples[tID]

def resolve(relative): 
   """Resolve a relative URI."""
   import os, urlparse
   pwd = os.environ.get('PWD')
   if pwd is None: 
      pwd = os.getcwd()
   if not pwd.endswith('/'): 
      pwd += '/'
   return urlparse.urljoin('file://' + pwd, relative)

class Graph(object): 
   counter = itertools.count(1)
   DefaultStore = Store

   def __init__(self, uri=None, baseURI=None, format=None): 
      self.ID = Graph.counter.next()

      # Graph(uri=None, parse=True, format=None)
      # 
      # Graph() - won't parse
      # Graph(uri) - will parse
      # Graph(uri, parse=False) - won't parse
      # Graph(uri, parse=link) - will parse
      # 
      # Graph() - no parse
      # Graph(uri) - parse
      # Graph(base=uri) - no parse
      # Graph(uri, base=uri) - parse

      # if uri is None: 
      #    if parse is False: PASS
      #    elif parse is True: SET TO FALSE
      #    else: ERROR
      #    SET URI TO SOME FAKE
      # elif uri is not None: 
      #    if parse is False: 
      #       JUST SET THE URI
      #    elif parse is True: 
      #       SET THE URI, PARSE IT
      #    else: SET THE URI, BUT PARSE PARSE

      # if uri and parse: 
      #    if parse is not None: 
      #       source = parse
      #    else: source = uri
      # elif uri and (parse is False)

      self.uri = uri
      self.baseURI = baseURI or self.uri

      self.format = format
      self.store = Graph.DefaultStore()

      if self.uri: 
         self.parseURI(self.uri)

   def __len__(self): 
      return len(self.store.triples)

   def __eq__(self, other): 
      if not isinstance(other, Graph): 
         return False
      if len(self) != len(other): 
         return False

      for bindings in self.__query(other, bind=self.__bind_iso): 
         return True
      return False

   def __ne__(self, other): 
      return (not self.__eq__(other))

   def __iter__(self): 
      return self.store.triples.itervalues()

   def __add__(self, other): 
      G = Graph()
      for triple in self: 
         G.store.add(triple)
      for triple in other: 
         G.store.add(triple)
      return G

   def nodes(self): 
      for subject in self.store.subjects.iterkeys(): 
         yield subject
      for object in self.store.objects.iterkeys(): 
         if not self.store.subjects.has_key(object): 
            yield object

   def arcs(self): 
      return self.store.predicates.iterkeys()

   # def subjects(self): 
   #    return self.store.subjects.iterkeys()

   # def predicates(self): 
   #    return self.store.predicates.iterkeys()

   # def objects(self): 
   #    return self.store.objects.iterkeys()

   def uri(self): 
      return self.__uri

   def __setURI(self, uri): 
      if uri and (not ':' in uri): 
         uri = resolve(uri)
      self.__uri = uri
   uri = property(uri, __setURI)

   def baseURI(self): 
      return self.__baseURI

   def __setBaseURI(self, baseURI): 
      if baseURI and (not ':' in baseURI): 
         raise ValueError('baseURI must be absolute')
      elif not (self.uri or baseURI): # Make an API-instance unique URI
         baseURI = 'http://inamidst.com/misc/graphs/' + str(self.ID)
         # @@! use some function of the PWD instead, like cwm
      self.__baseURI = baseURI
   baseURI = property(baseURI, __setBaseURI)

   # @@ None of the parse* methods are to merge
   # Make a new graph and add that if you want to do that
   def parseText(self, text, format=None): 
      from cStringIO import StringIO
      f = StringIO(text.encode('utf-8'))
      f.seek(0)
      self.parseFile(f, format=format)
      f.close()

   def parseFile(self, f, format=None): 
      if format is None: 
         if self.format is None: 
            if isinstance(f, web.Document): 
               self.format = f.format()
            else: raise ValueError('A format is required for parsing')
         format = self.format

      if format == 'rdfxml': 
         rdfxml.URI = URI
         rdfxml.bNode = BlankNode
         rdfxml.Literal = PlainLiteral
         rdfxml.DatatypedLiteral = TypedLiteral

         def callback(s, p, o, self=self): 
            triple = Triple(s, p, o)
            self.store.add(triple)
         rdfxml.parseFile(self.baseURI, f, callback=callback)

      elif format == 'turtle': 
         turtle.URI = URI
         turtle.bNode = BlankNode
         turtle.Literal = PlainLiteral
         turtle.DatatypedLiteral = TypedLiteral

         class Parser(turtle.TurtleDocument): 
            def triple(self, s, p, o, graph=self): 
               triple = Triple(s, p, o)
               graph.store.add(triple)
         doc = Parser(self.baseURI, f)
         doc.parse()

      elif format == 'n3': 
         notation3.URI = URI
         notation3.bNode = BlankNode
         notation3.PlainLiteral = PlainLiteral
         notation3.TypedLiteral = TypedLiteral
         notation3.Var = Variable

         def triple(s, p, o, self=self): 
            self.store.add(Triple(s, p, o))
         sink = notation3.RDFSink(triple=triple)
         p = notation3.SinkParser(sink, baseURI=self.baseURI)
         p._bindings[''] = p._baseURI + '#'
         p.startDoc()
         bytes = f.read()
         p.feed(bytes)
         # for line in f: 
         #    p.feed(line)
         p.endDoc()

      elif format == 'ntriples': # @@ n-triples
         ntriples.URI = URI
         ntriples.bNode = BlankNode
         ntriples.PlainLiteral = PlainLiteral
         ntriples.TypedLiteral = TypedLiteral
         ntriples.Var = Variable
         ntriples.extended = True # @@ ntriples-rdf? n-triples! (?)

         class Parser(ntriples.Document): 
            def triple(self, s, p, o, graph=self): 
               triple = Triple(s, p, o)
               graph.store.add(triple)
         doc = Parser(self.baseURI, f)
         doc.parse()

      elif format == 'sparql-results': 
         srx.URI = URI
         srx.bNode = BlankNode
         srx.Literal = PlainLiteral
         srx.DatatypedLiteral = TypedLiteral

         class Parser(srx.Document): 
            def triple(self, s, p, o, graph=self): 
               triple = Triple(s, p, o)
               graph.store.add(triple)
         import xml.dom.minidom
         doc = xml.dom.minidom.parse(f)
         p = Parser(doc)
         p.parse()

      elif format == 'grddl': 
         for triple in grddl.parse(self.baseURI): # @@ urgh
            self.store.add(triple) # @@ urgh...
      else: raise ValueError('Unsupported format: %s' % format)

   def parseURI(self, uri, format=None): 
      u = web.doc(uri)
      self.parseFile(u, format=format)
      u.close()      

   # def addGraph(self, G): 
   #    pass

   def serialiseToLines(self, format):
      if format == 'rdfxml':
         return serialise.rdfxml(self)
      elif format == 'ntriples':
         return serialise.ntriples(self)
      raise Exception('%s is unsupported' % format)

   def serialiseToText(self, format): 
      lines = self.serialiseToLines(format)
      return u'\n'.join(lines)

   def serialiseToFile(self, format, f): 
      for line in self.serialiseToLines(format): 
         print >> f, line
      return True

   def varSorted(self): 
      import heapq
      heap = []

      def rank(term): 
         if isinstance(term, Variable): return 4
         if isinstance(term, BlankNode): return 3
         return 0

      for t in self: 
         ranking = rank(t.subject) + rank(t.predicate) + rank(t.object)
         heapq.heappush(heap, (ranking, t))

      while heap: 
         ranking, t = heapq.heappop(heap)
         yield t

   def __bind(self, (s, p, o), result_triple, bindings): 
      new_bindings = bindings.copy()

      if s is not None: 
         bound = new_bindings.get(s)
         if bound is None: 
            new_bindings[s] = result_triple.subject
         elif bound != result_triple.subject: 
            return False # Prune mismatched bindings

      if p is not None: 
         bound = new_bindings.get(p)
         if bound is None: 
            new_bindings[p] = result_triple.predicate
         elif bound != result_triple.predicate: 
            return False # Prune mismatched bindings

      if o is not None: 
         bound = new_bindings.get(o)
         if bound is None: 
            new_bindings[o] = result_triple.object
         elif bound != result_triple.object: 
            return False # Prune mismatched bindings

      return new_bindings

   def __bind_iso(self, (s, p, o), result_triple, bindings): 
      new_bindings = bindings.copy()

      if s is not None: 
         bound = new_bindings.get(s)
         if bound is None: 
            if type(s) != type(result_triple.subject): 
               return False # Prune mismatched types
            new_bindings[s] = result_triple.subject
         elif bound != result_triple.subject: 
            return False # Prune mismatched bindings

      if p is not None: 
         bound = new_bindings.get(p)
         if bound is None: 
            if type(p) != type(result_triple.predicate): 
               return False # Prune mismatched types
            new_bindings[p] = result_triple.predicate
         elif bound != result_triple.predicate: 
            return False # Prune mismatched bindings

      if o is not None: 
         bound = new_bindings.get(o)
         if bound is None: 
            if type(o) != type(result_triple.object): 
               return False # Prune mismatched types
            new_bindings[o] = result_triple.object
         elif bound != result_triple.object: 
            return False # Prune mismatched bindings

      return new_bindings

   def __query(self, Q, bind=None): 
      # Returns a generator of simple bindings
      if bind is None: 
         bind = self.__bind

      def masks(triple): 
         try: return masks.cache[triple]
         except KeyError: pass

         s = isinstance(triple.subject, Var)
         p = isinstance(triple.predicate, Var)
         o = isinstance(triple.object, Var)

         qmask = ((not s and triple.subject), 
                  (not p and triple.predicate), 
                  (not o and triple.object))
         bmask = ((s and triple.subject or None), 
                  (p and triple.predicate or None), 
                  (o and triple.object or None))

         masks.cache[triple] = qmask, bmask
         return qmask, bmask
      masks.cache = {}

      def product(inputs, bindings=None): 
         if bindings is None: 
            bindings = {}

         if inputs: 
            query_triple = inputs[0]
            qmask, bmask = masks(query_triple)
            result_triples = self.store.get(*qmask)
            for result_triple in result_triples: 
               new_bindings = bind(bmask, result_triple, bindings)
               if new_bindings is False: continue

               for result_bindings in product(inputs[1:], new_bindings):
                  yield result_bindings
         else: yield bindings

      query_triples = list(Q.varSorted())
      return product(query_triples)

   def query(self, Q, *args, **params): 
      sort, get = params.pop('sort', None), params.pop('get', None)

      if params: raise ValueError('Params must be sort and/or get')
      if args and (sort or get): 
         raise ValueError("Can't have args *and* params")

      if args: sort, get = args[0], args
      if get and (len(get) == 1): 
         get = get[0]

      # Create a generator of simple name: value query bindings
      results = (dict((k.label, v) for (k, v) in bindings.iteritems()
                      if isinstance(k, Variable)) # Variables only!
                 for bindings in self.__query(Q))

      if sort: 
         def compare(a, b): 
            return cmp(a[sort], b[sort])
         results = sorted(results, cmp=compare)

      if not get: 
         return results

      if isinstance(get, basestring): 
         return (b[get] for b in results)
      return (tuple(b[g] for g in get) for b in results)

   def subgraphs(self, Q): 
      # Query, returning subgraphs not bindings
      pass

   def get(self, subject=None, predicate=None, object=None): 
      print >> __import__('sys').stderr, """\
      Warning: Graph.get is deprecated! Use Graph.triples instead.
      """
      return self.store.get(subject, predicate, object)

   def triples(self, subject=None, predicate=None, object=None): 
      return self.store.get(subject, predicate, object)

   def the(self, subject=None, predicate=None, object=None): 
      result = None
      for triple in self.store.get(subject, predicate, object): 
         if result is None: 
            result = triple
         else: raise ValueError('Expected only one result, got more')
      return result

   def select(self, Q, order=None): 
      # @@ Remove this when people have had enough warning
      print >> __import__('sys').stderr, """\
      WARNING: Graph.select is deprecated!

         for bindings in G.select(Q, order='name'): 
            print bindings.name

      Becomes instead:

         for bindings in G.query(Q, sort='name'): 
            print bindings['name']

      Or better yet:

         for name in G.query(Q, 'name'): 
            print name
      """

      class Bindings(object): 
         pass

      results = []
      for bindings in self.__query(Q): 
         b = Bindings()
         for (k, v) in bindings.iteritems(): 
            if isinstance(k, Variable): 
               attr = k.label
               setattr(b, attr, v)

         if order is None: 
            yield b
         else: results.append(b)

      if order is not None: 
         def compare(a, b): 
            return cmp(getattr(a, order).lexical, getattr(b, order).lexical)
         for b in sorted(results, cmp=compare): 
            yield b

   def sparql(self, bgp): 
      """Evaluate a sparql.BGP instance against this Graph."""
      import sparql
      Q = Graph()
      for triple in bgp: 
         t = Triple(*triple)
         Q.store.add(t)
      results = self.__query(Q)

      class Multiset(sparql.Multiset): 
         def graph(self): 
            R = Graph()
            R.sparqlMultiset(self)
            if False: # @@ debug
               for line in R.serialiseToLines(format='ntriples'): 
                  print line
            return R

      multiset = Multiset()
      for bindings in results: 
         mapping = sparql.SolutionMapping(bindings)
         multiset.add(mapping)
      return multiset

   def sparqlMultiset(self, multiset): 
      rdf = u'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
      rs = u'http://www.w3.org/2001/sw/DataAccess/tests/result-set#'
      rdf_type = URI(rdf + u'type')
      rs_ResultSet = URI(rs + u'ResultSet')
      rs_resultVariable = URI(rs + u'resultVariable')
      rs_solution = URI(rs + u'solution')
      rs_binding = URI(rs + u'binding')
      rs_value = URI(rs + u'value')
      rs_variable = URI(rs + u'variable')      

      counter = itertools.count(1)
      s = BlankNode(u'set' + str(counter.next()))
      self.store.add(Triple(s, rdf_type, rs_ResultSet))

      def literal(var): 
         return PlainLiteral(unicode(var.label))

      for i, solution in enumerate(multiset): 
         if i == 0: 
            for variable in solution.iterkeys(): 
               self.store.add(Triple(s, rs_resultVariable, literal(variable)))
         sol = BlankNode(u'solution' + str(counter.next()))
         self.store.add(Triple(s, rs_solution, sol))
         for (variable, value) in solution.iteritems(): 
            bin = BlankNode(u'binding' + str(counter.next()))
            self.store.add(Triple(sol, rs_binding, bin))
            self.store.add(Triple(bin, rs_variable, literal(variable)))
            self.store.add(Triple(bin, rs_value, value))             

   def sparqlFile(self, rq, form=None): 
      """Evaluate a SPARQL file, rq, with this as the default Graph."""
      import sparql
      D = sparql.Dataset(default=self)
      # sparql.debug = True
      sparql.IRI = URI
      sparql.Variable = Variable
      E, DS, R = sparql.parse(rq.read())

      if form is not None: 
         if R[0] != form: 
            raise ValueError("Expected %s, got %s" % (form, R[0]))

      if R[0] == 'SELECT': 
         result = sparql.evaluate(D, E)
         vars = R[1]
         if vars and ((len(vars) > 1) or (vars[0] != '*')): 
            vars = set(vars)
            selected = type(result)()
            for solution in result: 
               sol = type(solution)()
               for variable, value in solution.iteritems(): 
                  if variable in vars: 
                     sol[variable] = value
               selected.add(sol)
            result = selected
         elif not vars: 
            result = sparql.Multiset()
      else: raise ValueError('Not implemented: %s' % R[0])

      if form is not None: 
         return result
      return R[0], result

   def sparqlURI(self, uri, form=None): 
      import urllib
      u = urllib.urlopen(uri)
      result = self.sparqlFile(u, form=form)
      u.close()
      return result

class Term(object): 
   """Any Constant (URI, Literal) or Var (BlankNode, Variable)."""

class Constant(Term): 
   """Any URI or Literal (PlainLiteral, TypedLiteral)."""

Monotonous = Constant

class URI(Constant): 
   # @@ relative vs. absolute
   def __init__(self, value): 
      assert isinstance(value, unicode)
      self.value = value

   def encode(self): 
      # or self.uri()
      raise Exception('@@ Not implemented')

   def validate(self): 
      # "does not contain any control characters (#x00-#x1F, #x7F-#x9F)"
      # check for control characters, check that it converts to URI okay
      raise Exception('@@ Not implemented')

   def __repr__(self): 
      return 'URI(%r)' % self.value

   def __str__(self): 
      """Return a NON-N-TRIPLES string representation."""
      return '<' + self.value.encode('utf-8') + '>'

   def __hash__(self): 
      return hash(self.value) ^ 0x31337

   def __eq__(self, other): 
      # @@ <class 'trio.rdf.URI'> <class 'rdf.URI'> False
      # if not isinstance(other, URI): 
      if not hasattr(other, 'value'): 
         return False
      return self.value == other.value

   def __ne__(self, other): 
      if not isinstance(other, URI): 
         return True
      return self.value != other.value

   def __cmp__(self, other): 
      if isinstance(other, URI): 
         return cmp(self.value, other.value)
      return -1      

class URIReference(object): 
   # @@ relative vs. absolute
   def __init__(self, value): 
      print >> __import__('sys').stderr, """
      WARNING: trio.rdf.URIReference is deprecated. Use trio.rdf.URI instead.
      """
      assert isinstance(value, unicode)
      self.value = value

   def encode(self): 
      # or self.uri()
      raise Exception('@@ Not implemented')

   def validate(self): 
      # "does not contain any control characters (#x00-#x1F, #x7F-#x9F)"
      # check for control characters, check that it converts to URI okay
      raise Exception('@@ Not implemented')

   def __repr__(self): 
      return 'URIReference(%r)' % self.value

   def __str__(self): 
      """Return a NON-N-TRIPLES string representation."""
      return '<' + self.value.encode('utf-8') + '>'

   def __hash__(self): 
      return hash(self.value) ^ 0x31337

   def __eq__(self, other): 
      # @@ <class 'trio.rdf.URIReference'> <class 'rdf.URIReference'> False
      # if not isinstance(other, URIReference): 
      if not hasattr(other, 'value'): 
         return False
      return self.value == other.value

   def __ne__(self, other): 
      if not isinstance(other, URIReference): 
         return True
      return self.value != other.value

   def __cmp__(self, other): 
      if isinstance(other, URIReference): 
         return cmp(self.value, other.value)
      return -1      

class Literal(Constant): 
   """An RDF Literal."""

# All literals have a lexical form being a Unicode [UNICODE] string, which 
# SHOULD be in Normal Form C [NFC].

class PlainLiteral(Literal): 
   """An RDF Plain Literal."""

   def __init__(self, lexical, language=None): 
      self.lexical = unicodedata.normalize('NFC', lexical)
      self.language = language

   def __hash__(self): 
      return hash(self.lexical) ^ hash(self.language) ^ 0x31337

   def __eq__(self, other): 
      if not isinstance(other, PlainLiteral): 
         return False
      if (self.lexical == other.lexical) and \
         (self.language == other.language): 
         return True
      return False

   def __ne__(self, other): 
      if not isinstance(other, PlainLiteral): 
         return True
      if (self.lexical == other.lexical) and \
         (self.language == other.language): 
         return False
      return True

   def __cmp__(self, other): 
      if isinstance(other, URI): 
         return 1
      elif isinstance(other, PlainLiteral): 
         return cmp((self.lexical, self.language), 
                    (other.lexical, other.language))
      return -1

   def __repr__(self): 
      return 'PlainLiteral(%r, %r)' % (self.lexical, self.language)

   def __str__(self): 
      """Return a NON-N-TRIPLES string representation."""
      s = '"' + self.lexical.encode('utf-8') + '"'
      if not self.language: 
         return s
      else: return s + '@' + self.language.encode('utf-8')

class TypedLiteral(Literal): 
   """An RDF Typed Literal."""

   def __init__(self, lexical, datatype): 
      self.lexical = unicodedata.normalize('NFC', lexical)
      assert isinstance(datatype, URI)
      self.datatype = datatype

   def __hash__(self): 
      return hash(self.lexical) ^ hash(self.datatype) ^ 0x31337

   def __eq__(self, other): 
      # This is *lexical* comparison, not value comparison
      if not isinstance(other, TypedLiteral): 
         return False
      if (self.lexical == other.lexical) and \
         (self.datatype == other.datatype): 
         return True
      return False

   def __ne__(self, other): 
      return (not self.__eq__(other))

   def __cmp__(self, other): 
      if isinstance(other, URI): 
         return 1
      elif isinstance(other, PlainLiteral): 
         return 1
      elif isinstance(other, TypedLiteral): 
         return cmp((self.lexical, self.datatype), 
                    (other.lexical, other.datatype))
      return -1

   def __repr__(self): 
      return 'TypedLiteral(%r, %r)' % (self.lexical, self.datatype)

   def __str__(self): 
      """Return a NON-N-TRIPLES string representation."""
      s = '"' + self.lexical.encode('utf-8') + '"'
      if not self.datatype: 
         return s
      else: return s + '^^' + str(self.datatype)

class Var(Term): 
   """Any BlankNode or Variable."""

Ticklish = Var

class BlankNode(Var): 
   def __init__(self, label): 
      self.label = label

   def __repr__(self): 
      return 'BlankNode(%r)' % self.label

   def __str__(self): 
      """Return a NON-N-TRIPLES string representation."""
      return '_:' + self.label.encode('utf-8')

   def __hash__(self): 
      return hash(self.label) ^ 0x31337

   def __eq__(self, other): 
      if not isinstance(other, BlankNode): 
         return False
      return self.label == other.label

   def __ne__(self, other): 
      if not isinstance(other, BlankNode): 
         return True
      return self.label != other.label

   def __cmp__(self, other): 
      if isinstance(other, URI): 
         return 1
      elif isinstance(other, PlainLiteral): 
         return 1
      elif isinstance(other, TypedLiteral): 
         return 1
      elif isinstance(other, BlankNode): 
         return cmp(self.label, other.label)
      return -1

class Variable(Var): 
   def __init__(self, label): 
      self.label = label

   def __repr__(self): 
      return 'Variable(%r)' % self.label

   def __hash__(self): 
      return hash(self.label) ^ 0x31337

   def __eq__(self, other): 
      if not isinstance(other, Variable): 
         return False
      return self.label == other.label

   def __ne__(self, other): 
      if not isinstance(other, Variable): 
         return True
      return self.label != other.label

   def __cmp__(self, other): 
      if isinstance(other, URI): 
         return 1
      elif isinstance(other, PlainLiteral): 
         return 1
      elif isinstance(other, TypedLiteral): 
         return 1
      elif isinstance(other, BlankNode): 
         return 1
      elif isinstance(other, Variable): 
         return cmp(self.label, other.label)
      return -1

class N3(object): 
   # Notation3 Environment
   def __init__(self): 
      # @@ IRIs
      self.bindings = {
         'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#', 
         'rdfs': 'http://www.w3.org/2000/01/rdf-schema#', 
         'owl': 'http://www.w3.org/2002/07/owl#', 
         'dc': 'http://purl.org/dc/elements/1.1/', 
         'foaf': 'http://xmlns.com/foaf/0.1/', 
         'doap': 'http://usefulinc.com/ns/doap#', 
         'skos': 'http://www.w3.org/2004/02/skos/core#'
      }

   def __call__(self, text, baseURI=None): 
      if not text.rstrip(' \t\r\n').endswith('.'): 
         text += ' .'
      prefixes = '\n'.join(
         '@prefix %s: <%s> .' % pair for pair in self.bindings.iteritems()
      ) + '\n@keywords a, is, of .\n\n'
      G = Graph(baseURI=baseURI)
      G.parseText(prefixes + text, format='n3')
      return G

   def __getitem__(self, qname): 
      if ':' in qname: 
         prefix, localname = qname.split(':')
      else: prefix, localname = '', qname
      namespace = self.bindings[prefix]
      return URI(unicode(namespace) + localname)

   def prefix(self, localname, uri): 
      self.bindings[localname] = uri

n3 = N3()

class Commands(object): 
   def __init__(self): 
      pass

   def format(self, uri): 
      resp = web.doc(uri)
      result = resp.format()
      resp.close()
      return result or 'unknown'

commands = Commands()

# EOF
