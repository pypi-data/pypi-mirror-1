from Acquisition import aq_parent
from Products.Five import BrowserView
from Products.Five.site.localsite import enableLocalSiteHook, disableLocalSiteHook
from rhizome.interfaces import IRDFStore
from rhizome.five.store import OFSRhizomeStore
from zope import component as zcomp
from zope.app.component.hooks import setSite, setHooks
from zope.app.component.interfaces import ISite, IPossibleSite
from zope.component.interfaces import ComponentLookupError
from zope.interface import implements, implementer
from OFS.interfaces import IApplication
from rhizome.utils import any

# convenience functions
def add_rhizome(site, findroot=False):
    addUtility(site, IRDFStore, OFSRhizomeStore, findroot=findroot)

def get_rhizome(context=None):
    return zcomp.getUtility(IRDFStore, context=context)

def del_rhizome(context=None, findroot=False):
    if findroot:
        context = get_root(context)
    utility = get_rhizome(context)
    parent = utility.aq_parent
    parent.manage_delObjects([utility.getId()])

class RhizomeInstallView(BrowserView):
    """ installer view """

    add_rhizome=staticmethod(add_rhizome)
    get_rhizome=staticmethod(get_rhizome)   
    
    @property
    def context(self):
        return self._context[0]
    
    def __init__(self, context, request):
        self._context = context,
        self.request = request
        doinstall = self.request.get('install-rhizome', None)
        if doinstall:
            self.install_rhizome()

    def install_rhizome(self):
        self.add_rhizome(self.context)

    @property
    def installed(self):
        installed = False
        try:
            rhizome = self.get_rhizome(self.context)
            if rhizome:
                installed = True
        except ComponentLookupError, e:
            pass
        return installed
    
def initializeSite(site, sethook=False, **kw):
    enableLocalSiteHook(site)
    if sethook:
         setHooks()
    setSite(site)

def addUtility(site, interface, klass, name='', findroot=True):
    """
    add local utility in zope2
    """
    app = site
    if findroot:
        app = get_root(site)
    else:
        site = get_site(site)
    assert app, TypeError("app is None")

    if not ISite.providedBy(app):
        initializeSite(app, sethook=False)
        
    sm = app.getSiteManager()
    if sm.queryUtility(interface,
                       name=name,
                       default=None) is None:

        if name: obj = klass(name)
        else: obj = klass()
        sm.registerUtility(interface, obj, name=name)  #2.9

def get_root(app):
    # adapted from alecm's 'listen'
    while app is not None and not IApplication.providedBy(app):
            app = aq_parent(app)
    return app

def get_site(site):
    while site is not None and not (ISite.providedBy(site) or IPossibleSite.providedBy(site)):
        site = aq_parent(site)
    return site
    


