from rdf.parser import Parser

from rdf.term import URIRef, BNode, Literal, Variable
from rdf.graph import Graph, QuotedGraph, ConjunctiveGraph

from rdf.plugins.parsers.n3p.n3proc import N3Processor
#from n3p.n3proc import N3Processor
#from n3proc import N3Processor



class N3(Parser):

    def __init__(self):
        pass

    def parse(self, source, graph):
        # we're currently being handed a Graph, not a ConjunctiveGraph
        assert graph.store.context_aware, "graph not context aware as required"
        assert graph.store.formula_aware, "graph not formula aware as required"

        conj_graph = ConjunctiveGraph(store=graph.store)
        conj_graph.default_context = graph # TODO: CG __init__ should have a default_context arg
        # TODO: update N3Processor so that it can use conj_graph as the sink
        sink = Sink(conj_graph)
        if False:
            sink.quantify = lambda *args: True
            sink.flatten = lambda *args: True
        baseURI = graph.absolutize(source.getPublicId() or source.getSystemId() or "")
        p = N3Processor("nowhere", sink, baseURI=baseURI) # pass in "nowhere" so we can set data instead
        p.userkeys = True # bah
        p.data = source.getByteStream().read() # TODO getCharacterStream?
        p.parse()
        for prefix, namespace in p.bindings.items():
            conj_graph.bind(prefix, namespace)


class Sink(object):
    def __init__(self, graph):
        self.graph = graph

    def start(self, root):
        pass

    def statement(self, s, p, o, f):
        f.add((s, p, o))

    def quantify(self, formula, var):
        #print "quantify(%s, %s)" % (formula, var)
        pass

