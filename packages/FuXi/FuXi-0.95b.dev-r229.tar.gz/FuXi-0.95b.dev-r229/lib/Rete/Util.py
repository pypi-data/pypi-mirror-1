"""
Utility functions for a Boost Graph Library (BGL) DiGraph via the BGL Python Bindings
"""
from FuXi.Rete.AlphaNode import AlphaNode

try:    
    import boost.graph as bgl
    bglGraph = bgl.Digraph()
except:
    try:
        from pydot import Node,Edge,Dot
    except:
        import warnings
        warnings.warn("Missing pydot library",ImportWarning)        
        #raise NotImplementedError("Boost Graph Library & Python bindings (or pydot) not installed.  See: see: http://www.osl.iu.edu/~dgregor/bgl-python/")
        
from rdflib.Graph import Graph
from rdflib.syntax.NamespaceManager import NamespaceManager
from rdflib import BNode, Namespace, Collection, Variable
from sets import Set

LOG = Namespace("http://www.w3.org/2000/10/swap/log#")

def xcombine(*seqin):
    '''
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/302478
    returns a generator which returns combinations of argument sequences
    for example xcombine((1,2),(3,4)) returns a generator; calling the next()
    method on the generator will return [1,3], [1,4], [2,3], [2,4] and
    StopIteration exception.  This will not create the whole list of 
    combinations in memory at once.
    '''
    def rloop(seqin,comb):
        '''recursive looping function'''
        if seqin:                   # any more sequences to process?
            for item in seqin[0]:
                newcomb=comb+[item]     # add next item to current combination
                # call rloop w/ remaining seqs, newcomb
                for item in rloop(seqin[1:],newcomb):   
                    yield item          # seqs and newcomb
        else:                           # processing last sequence
            yield comb                  # comb finished, add to list
    return rloop(seqin,[])

def permu(xs):
    """
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/496819
    "A recursive function to get permutation of a list"
    
    >>> print list(permu([1,2,3]))
    [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]
     
    """
    if len(xs) <= 1:
        yield xs
    else:
        for i in range(len(xs)):
            for p in permu(xs[:i] + xs[i + 1:]):
                yield [xs[i]] + p

def generateTokenSet(graph,debugTriples=[],skipImplies=True):
    """
    Takes an rdflib graph and generates a corresponding Set of ReteTokens
    Note implication statements are excluded from the realm of facts by default
    """
    from FuXi.Rete import ReteToken
    rt = Set()    
    def normalizeGraphTerms(term):
        if isinstance(term,Collection.Collection):
            return term.uri
        else:
            return term
    for s,p,o in graph:
        
        if not skipImplies or p != LOG.implies:
            #print s,p,o             
            debug = debugTriples and (s,p,o) in debugTriples
            rt.add(ReteToken((normalizeGraphTerms(s),
                              normalizeGraphTerms(p),
                              normalizeGraphTerms(o)),debug))
    return rt

def generateBGLNode(dot,node,namespace_manager,identifier):
    from FuXi.Rete import ReteNetwork,BetaNode,BuiltInAlphaNode,AlphaNode
    from BetaNode import LEFT_MEMORY, RIGHT_MEMORY, LEFT_UNLINKING
    vertex = Node(identifier)

    shape = 'circle'
    root        = False
    if isinstance(node,ReteNetwork):     
        root        = True
        peripheries = '3'
    elif isinstance(node,BetaNode) and not node.consequent:     
        peripheries = '1'
        if node.aPassThru:
            label = "Pass-thru Beta node\\n"
        elif node.commonVariables:
            label = "Beta node\\n(%s)"%(','.join(["?%s"%i for i in node.commonVariables]))
        else:
            label = "Beta node"

    elif isinstance(node,BetaNode) and node.consequent:     
        #rootMap[vertex] = 'true'
        peripheries = '2'
        stmts = []
        for s,p,o in node.consequent:
            stmts.append(' '.join([str(namespace_manager.normalizeUri(s)),
              str(namespace_manager.normalizeUri(p)),
              str(namespace_manager.normalizeUri(o))]))
              
        rhsVertex = Node(BNode(),
                         label='"'+'\\n'.join(stmts)+'"',
                         shape='plaintext') 
        edge = Edge(vertex,rhsVertex)
        #edge.color = 'red'
        dot.add_edge(edge)              
        dot.add_node(rhsVertex)      
        if node.commonVariables:
            label = str("Terminal node\\n(%s)"%(','.join(["?%s"%i for i in node.commonVariables])))
        else:
            label = "Terminal node"
        
    elif isinstance(node,BuiltInAlphaNode):
        peripheries = '1'
        shape = 'plaintext'
        #label = '..Builtin Source..'
        label = repr(node.n3builtin)
        canonicalFunc = namespace_manager.normalizeUri(node.n3builtin.uri)
        canonicalArg1 = namespace_manager.normalizeUri(node.n3builtin.argument)
        canonicalArg2 = namespace_manager.normalizeUri(node.n3builtin.result)
        label = '%s(%s,%s)'%(canonicalFunc,canonicalArg1,canonicalArg2)
        
    elif isinstance(node,AlphaNode):
        peripheries = '1'
        shape = 'plaintext'
#        widthMap[vertex] = '50em'
        label = ' '.join([isinstance(i,BNode) and i.n3() or str(namespace_manager.normalizeUri(i)) 
                           for i in node.triplePattern])    

    vertex.set_shape(shape)
    vertex.set_label('"%s"'%label)
    vertex.set_peripheries(peripheries)
    if root:
        vertex.set_root('true')
    return vertex

def renderNetwork(network,nsMap = {}):
    """
    Takes an instance of a compiled ReteNetwork and a namespace mapping (for constructing QNames
    for rule pattern terms) and returns a BGL Digraph instance representing the Rete network
    #(from which GraphViz diagrams can be generated)
    """
    from FuXi.Rete import BuiltInAlphaNode
    from BetaNode import LEFT_MEMORY, RIGHT_MEMORY, LEFT_UNLINKING
    dot=Dot(graph_type='digraph')
    namespace_manager = NamespaceManager(Graph())
    for prefix,uri in nsMap.items():
        namespace_manager.bind(prefix, uri, override=False)

    visitedNodes = {}
    edges = []
    idx = 0
    for node in network.nodes.values():
        if not node in visitedNodes and not isinstance(node,BuiltInAlphaNode):
            idx += 1
            visitedNodes[node] = generateBGLNode(dot,node,namespace_manager,str(idx))
            dot.add_node(visitedNodes[node])
    nodeIdxs = {}                        
    for node in network.nodes.values():
        for mem in node.descendentMemory:
            if not mem:
                continue
            bNode = mem.successor
        for bNode in node.descendentBetaNodes:
            for otherNode in [bNode.leftNode,bNode.rightNode]:
                if node == otherNode and (node,otherNode) not in edges:
                    for i in [node,bNode]:
                        if i not in visitedNodes:
                            idx += 1
                            nodeIdxs[i] = idx 
                            visitedNodes[i] = generateBGLNode(dot,i,namespace_manager,str(idx))
                            dot.add_node(visitedNodes[i])
                    edge = Edge(visitedNodes[node],visitedNodes[bNode])
                    dot.add_edge(edge)                                        
                    edges.append((node,bNode))
                    
    return dot

def test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    test()    