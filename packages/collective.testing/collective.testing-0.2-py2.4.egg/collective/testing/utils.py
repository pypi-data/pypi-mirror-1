from zope.testing.cleanup import cleanUp
from zope.publisher.browser import TestRequest

class RESPONSE(object):
    
    def __init__(self):
        self.headers = dict()
        
    def redirect(self, url, lock=None):
        self.status=302
        self.headers['location']=url
        self.lock = lock

def new_request(**kwargs):
    request = TestRequest(form=kwargs)
    request.RESPONSE=RESPONSE()
    return request


def setDebugMode(mode):
    """
    Allows manual setting of Five's inspection of debug mode to allow for
    zcml to fail meaningfully
    """
    import Products.Five.fiveconfigure as fc
    fc.debug_mode = mode


def safe_load_site():
    """Load entire component architecture (w/ debug mode on)"""
    cleanUp()
    setDebugMode(1)
    import Products.Five.zcml as zcml
    zcml.load_site()
    setDebugMode(0)


def safe_load_site_wrapper(function):
    """Wrap function with a temporary loading of entire component architecture"""
    def wrapper(*args, **kw):
        safe_load_site()
        value = function(*args, **kw)
        cleanUp()
        import Products.Five.zcml as zcml
        zcml._initialized = 0
        return value
    return wrapper


def monkeyAppAsSite():
    # the python equivalent of load app as a localsite via zcml
    # import and call if you want to be able to treat the 
    import OFS.Application 
    from Products.Five.site.metaconfigure import classSiteHook
    from Products.Five.site.localsite import FiveSite

    from zope.interface import classImplements
    from zope.app.component.interfaces import IPossibleSite, ISite
    classSiteHook(OFS.Application.Application, FiveSite)
    classImplements(OFS.Application.Application, IPossibleSite)


def newuser():
    """ loads up an unrestricted security manager"""
    from AccessControl.SecurityManagement import newSecurityManager
    from AccessControl.User import UnrestrictedUser
    newSecurityManager( {}, UnrestrictedUser('debug', 'debug', [], [] ))

