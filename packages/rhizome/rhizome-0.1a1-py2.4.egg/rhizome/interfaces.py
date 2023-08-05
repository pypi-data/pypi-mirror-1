from zope.interface import Interface, Attribute
from zope.interface.common.sequence import IReadSequence as ITuple

class IRDFStore(Interface):
    """rhizome is a wrapper for a complementary set of rdflib graphs
    and stores"""
    
    _store = Attribute("primary persistent store for rdf")

    _index = Attribute("persistent store for text indexing")

    graph = Attribute("the store as a Conjunctive Graph")

    index = Attribute("index store wrapped in a TextIndex Graph")

    eventgraph = Attribute("primary store wrapped in a EventGraph")
    
    graph_index = Attribute(\
        "tuple of the eventgraph and the index graph (w/ the index"
        "subscribed to the eventgraph)")

    sparql = Attribute("primary graph wrapped as a SPARQL graph")

    def query(select, where):
        """convenience method for submitting GraphPattern queries"""


class IRDFData(ITuple):
    """
    An IRDFData object is a tuplish or
    tuplish object composed of triples representing data
    interesting about an object for IRhizome.
    """


class IRDFCatalogData(IRDFData):
    """ A dispatch interface: Should generally represent complete set
    of rdf data to be cataloged."""

    
class IRDFCatalogDataSubset(IRDFCatalogData):
    """
    to be subclassed by dispatch interfaces.

    A subset of the complete set of rdf data(ie for updates).
    """


class ISPARQLQuery(IRDFData):
    """
    A query object: a tuple of tuples representing the graph pattern
    """
    select = Attribute("the elements to return")
    factory = Attribute("bindery for return")
