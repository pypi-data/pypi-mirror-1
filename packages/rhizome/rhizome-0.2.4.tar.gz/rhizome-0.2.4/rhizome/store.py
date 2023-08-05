from BTrees.OOBTree import OOBTree
from persistent import Persistent
from rdflib import StringInputSource
from rdflib.Graph import ConjunctiveGraph as rdflibGraph
from rdflib.store import ZODB as ZODBBackend
from rdflib.TextIndex import TextIndexGraph 
from rdflib import EventGraph
import zope.cachedescriptors.property
from rdflib.sparql import SPARQLGraph, GraphPattern
from zope.interface import implements
from rhizome.interfaces import IRDFStore

class Rhizome(Persistent):
    implements(IRDFStore)
    
    def __init__(self, id_=IRDFStore.__name__):
        super(Rhizome, self).__init__(self, id_)
        self.id = id_
        self._store = ZODBBackend.ZODB()
        self._index = ZODBBackend.ZODB()

    @zope.cachedescriptors.property.Lazy 
    def graph(self):
        """
        @return: A RDFLib Graph
        @rtype: Graph
        """
        return rdflibGraph(self._store)

    @zope.cachedescriptors.property.Lazy 
    def index(self):
        """
        @return: A RDFLib TextIndex Graph
        @rtype: TextIndexGraph

        A TIG is a normal graph with a bit more logic.  There is no
        addIndex, use addGraph.
        """
        return TextIndex.TextIndexGraph(self._index)

    @zope.cachedescriptors.property.Lazy 
    def eventgraph(self):
        """
        @return: A RDFLib Event Graph
        @rtype: EventConjunctiveGraph
        """
        return EventGraph.EventConjunctiveGraph(self._store)

    @zope.cachedescriptors.property.Lazy 
    def graph_index(self):
        """
        Return a two-tuple of a graph and an index, with the index
        subscribed automatically to the graph.  Statements that are
        added to the graph are then automatically indexed.
        """
        self.index.subscribe_to(g)
        return self.eventgraph, self.index

    @zope.cachedescriptors.property.Lazy 
    def sparql(self):
        return SPARQLGraph(self.graph)

    def query(self, select, where):
        return self.sparql.query(select, GraphPattern(where))
