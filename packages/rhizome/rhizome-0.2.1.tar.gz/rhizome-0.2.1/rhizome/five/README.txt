==============
 rhizome.five
==============

Five is the zope3 for zope2 integration layer and likewhise,
rhizome.five is the compatibility layer that lets rhizome play in
zope2.

`rhizome.five.site` provides a basic convenience functions for
managing rhizome stores::

    >>> from rhizome.five.site import add_rhizome
    >>> add_rhizome(self.folder)
    >>> self.folder.utilities.objectIds()
    ['IRDFStore']

    >>> from rhizome.five.site import get_rhizome
    >>> get_rhizome(self.folder)
    <OFSRhizomeStore at /test_folder_1_/utilities/IRDFStore>

    >>> from rhizome.five.site import del_rhizome
    >>> del_rhizome(self.folder)
    >>> self.folder.utilities.objectIds()
    []
