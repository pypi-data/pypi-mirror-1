from OFS.SimpleItem import SimpleItem
from rhizome.store import Rhizome
from rhizome.interfaces import IRDFStore
from zope.interface import implements
from Globals import InitializeClass

class OFSRhizomeStore(Rhizome, SimpleItem):
    implements(IRDFStore)

InitializeClass(OFSRhizomeStore)
