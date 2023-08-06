#!/usr/local/env/python
#############################################################################
# Name:         bop
# Purpose:      Help methods, useful generic functions
# Maintainer:
# Copyright:    (c) 2004 iwm-kmrc.de KMRC - Knowledge Media Research Center
# Licence:      GPL
#############################################################################
__docformat__ = 'restructuredtext'

import sys, os, re, string, logging, time, cgi, errno
import os.path

import zope.app.file.interfaces
import zope.app.container.interfaces
import zope.app.file.image
import zope.contenttype

import zope.traversing.browser
import zope.i18n

from zope.component import ComponentLookupError
from zope.app.security.interfaces import PrincipalLookupError
from zope.publisher.interfaces import IRequest
from zope.publisher.browser import TestRequest
from zope.security.checker import Checker, CheckerPublic
from zope.security.management import queryInteraction
from zope.security.interfaces import ForbiddenAttribute
from zope.security.interfaces import Unauthorized
from zope.security.proxy import removeSecurityProxy
from zope.security import canAccess, canWrite
from zope.traversing.interfaces import IPhysicallyLocatable
from zope.app import zapi

from bebop.protocol.protocol import GenericFunction

import interfaces

here = os.path.dirname(__file__)

if sys.platform == 'win32':
    import win32file        #needed for oslink below

def url(context, request):
    try:
        return zope.traversing.browser.absoluteURL(context, request)
    except TypeError, msg:
        warning("%s: %s" % (context.__class__.__name__, msg))
        return None    

defaultRequest = None

def request(test=False) :
    global defaultRequest
    interaction = queryInteraction()
    if interaction is not None:
        for participation in interaction.participations:
            if IRequest.providedBy(participation) :
                return participation
    
    if test:
        return TestRequest()
    return defaultRequest
    
def setrequest(request) :
    global defaultRequest
    defaultRequest = request
        
def translate(text, domain='bebop'):
    if isinstance(text, zope.i18n.Message):
        return zope.i18n.translate(text, context=request(), domain=domain)
    return text

def traverse(obj):
    req = request()
    if req is None:
        return None
    return req.traverse(obj)

def traversePath(container, relpath):
    return zapi.traverse(container, relpath, request=request())
    
defaultUser = None

def userid():
    global defaultUser   
    if defaultUser is not None :
        return defaultUser
    request = request(test=False)
    if request is not None :
        return request.principal.id
 
def setuserid(id):
    global defaultUser
    defaultUser = id
    
def fullname(principal_id) :
    """ Returns the full name or title of a principal that can be used
        for better display.
        
        Returns the id if the full name cannot be found.
    """
    try :
        return zapi.principals().getPrincipal(principal_id).title
    except (PrincipalLookupError, AttributeError, ComponentLookupError) :
        return principal_id

def short(item, maxlen=None):
    if maxlen is not None and len(item) > maxlen:
        return item[:maxlen] + "..." 
    return item 

# util functions

def alwaysTrue(*args, **kw):
    return True

def parseQuery(request):
    """ Parses the query string."""
    try :
        if 'QUERY_STRING' in request :
            return cgi.parse_qs(request['QUERY_STRING'])
    except TypeError :
        pass
    return {}
               
def parameter(request, key, type=None, default=None):
    """Extracts a parameter from a request."""
    value = None
    if key in request :
        value = request[key]
    else:
        args = parseQuery(request)
        if key in args :
            value = args[key][0]
    if value is None :
        return default
    if type is None :
        if isinstance(value, str):
            value = unicode(value, encoding="utf-8")
    else :
        value = type(value)
    return value
        
def dottedname(cls, jsonsafe=True):
    dn = "%s.%s" % (cls.__module__, cls.__name__)
    if jsonsafe:
        return dn.replace('Null', 'Nul')
    return dn

def extension(filename):
    return os.path.splitext(filename)[1]
    
def guessContentType(filename, data=''):
    content_type = zope.contenttype.guess_content_type(filename, data, None)
    if content_type is not None :
        return content_type[0]
    return ''

def canAccessPage(context, request, page_name):
    view = zope.component.queryMultiAdapter(
                (context, request), name=page_name)
    return canAccess(view, '__call__')
        
def canManageContent(context):
    """ Is the user allowed to manage the content of the site?"""
    if zope.app.file.interfaces.IFile.providedBy(context):
        context = context.__parent__
    if zope.app.container.interfaces.IContainer.providedBy(context):
        try :
            return canAccess(context, '__setitem__')
        except ForbiddenAttribute :
            return False
    return False

def canAccessSiteManager(context):
    """ Is the user allowed to access the site management tools?"""
    locatable = IPhysicallyLocatable(context, None)
    if locatable is None:
        return False
    site = locatable.getNearestSite()
    try:
        # the ++etc++ namespace is public this means we get the sitemanager
        # without permissions. But this does not mean we can access it
        # Right now we check the __getitem__ method on the sitemamanger
        # but this means we don't show the ++etc++site link if we have
        # registred views on the sitemanager which have other permission
        # then the __getitem__ method form the interface IReadContainer
        # in the LocalSiteManager.
        # If this will be a problem in the future, we can add a 
        # attribute to the SiteManager which we can give individual 
        # permissions and check it via canAccess.        
        sitemanager = site.getSiteManager()
        authorized = canAccess(sitemanager, '__getitem__')
        if authorized:
            return True
        else:
            return False
    except ComponentLookupError:
        return False
    except ForbiddenAttribute :
        return False
    except AttributeError:
        return False
    except TypeError:
        # we can't check unproxied objects, but unproxied objects
        # are public.
        return True

evilChars = ' ,;'

def validFilename(filename):
    if '\\' in filename :   # grr, IE hack.
        filename = filename.split('\\')[-1]
    else:
        filename = os.path.basename(filename)
    for char in evilChars:
        filename = filename.replace(char, '_')
    return filename

        
# logging support

logger = logging.getLogger("Bebop.logger")

def warning(msg):
    """ Log warnings. """
    try :
        logger.warning(msg)
    except :
        print "Could not log bop.warning"
 
def info(msg):
    """ Log info. """
    try :
        logger.info(msg)
    except :
        print "Could not log bop.info"


deletable = GenericFunction('bop.helper.IDeletable')
@deletable.when(zope.interface.Interface, zope.interface.Interface)
def default_deletable(obj, request):
    return True    
    
editable = GenericFunction('bop.helper.IEditable')
@editable.when(zope.interface.Interface, zope.interface.Interface)
def default_editable(obj, request):
    return False    

@editable.when(zope.app.file.interfaces.IFile, zope.interface.Interface)
def file_editable(obj, request):
    return obj.contentType == 'text/html'
       

# filenames

validChars = string.letters + string.digits + '.+-'

def latin2ascii (unicrap):
    """This takes a UNICODE string and replaces Latin-1 characters with
    something equivalent in 7-bit ASCII. It returns a plain ASCII string. 
    This function makes a best effort to convert Latin-1 characters into 
    ASCII equivalents. It does not just strip out the Latin-1 characters.
    All characters in the standard 7-bit ASCII range are preserved. 
    In the 8th bit range all the Latin-1 accented letters are converted 
    to unaccented equivalents. Most symbol characters are converted to 
    something meaningful. Anything not converted is deleted.
    """
    xlate={0xc0:'A', 0xc1:'A', 0xc2:'A', 0xc3:'A', 0xc4:'Ae', 0xc5:'A',
        0xc6:'Ae', 0xc7:'C', 
        0xc8:'E', 0xc9:'E', 0xca:'E', 0xcb:'E',
        0xcc:'I', 0xcd:'I', 0xce:'I', 0xcf:'I',
        0xd0:'Th', 0xd1:'N',
        0xd2:'O', 0xd3:'O', 0xd4:'O', 0xd5:'O', 0xd6:'Oe', 0xd8:'O',
        0xd9:'U', 0xda:'U', 0xdb:'U', 0xdc:'Ue',
        0xdd:'Y', 0xde:'th', 0xdf:'ss',
        0xe0:'a', 0xe1:'a', 0xe2:'a', 0xe3:'a', 0xe4:'ae', 0xe5:'a',
        0xe6:'ae', 0xe7:'c',
        0xe8:'e', 0xe9:'e', 0xea:'e', 0xeb:'e',
        0xec:'i', 0xed:'i', 0xee:'i', 0xef:'i',
        0xf0:'th', 0xf1:'n',
        0xf2:'o', 0xf3:'o', 0xf4:'o', 0xf5:'o', 0xf6:'oe', 0xf8:'o',
        0xf9:'u', 0xfa:'u', 0xfb:'u', 0xfc:'ue',
        0xfd:'y', 0xfe:'th', 0xff:'y',
        0xa1:'!', 0xa2:'{cent}', 0xa3:'{pound}', 0xa4:'{currency}',
        0xa5:'{yen}', 0xa6:'|', 0xa7:'{section}', 0xa8:'{umlaut}',
        0xa9:'{C}', 0xaa:'{^a}', 0xab:'<<', 0xac:'{not}',
        0xad:'-', 0xae:'{R}', 0xaf:'_', 0xb0:'{degrees}',
        0xb1:'{+/-}', 0xb2:'{^2}', 0xb3:'{^3}', 0xb4:"'",
        0xb5:'{micro}', 0xb6:'{paragraph}', 0xb7:'*', 0xb8:'{cedilla}',
        0xb9:'{^1}', 0xba:'{^o}', 0xbb:'>>', 
        0xbc:'{1/4}', 0xbd:'{1/2}', 0xbe:'{3/4}', 0xbf:'?',
        0xd7:'*', 0xf7:'/'
        }

    r = ''
    for i in unicrap:
        if xlate.has_key(ord(i)):
            r += xlate[ord(i)]
        elif ord(i) >= 0x80:
            pass
        else:
            r += str(i)
    return r

def asciiName(name, allowed=validChars) :
    """Converts unicode filenames to ascii filenames. 
    
    Blanks and other special chars are translated to underscores.
    
    >>> ascii(u'\xdcberblick, der...')
    'Ueberblick__der...'
        
    """
    if isinstance(name, unicode):
        name = latin2ascii(name)
        for x in name :
            if x not in allowed :
                name = name.replace(x, "_")
            
    if '\\' in name :               # grr, IE hack
        return name.split('\\')[-1]
    return name
 
def public():
    """Declares a function as public."""
    def ensure_checker_public(f):
        name = f.func_name
        module = sys.modules[f.__module__]
        if not hasattr(module, '__Security_checker__'):
            module.__Security_checker__ = Checker({})
        sc = module.__Security_checker__
        sc.get_permissions[name] = CheckerPublic
        return f
    return ensure_checker_public

# debugging

def debug(*args):
    for item in args:
        print >>sys.__stdout__, item,
    print >>sys.__stdout__, ""

def printTrace(warning="shouldn't happen"):
    """ Print diagnostic output after an caught exception """
    import traceback, sys, string
    info = sys.exc_info()
    tb = info[2]
    exception_log = traceback.format_exception(sys.exc_type, sys.exc_value,tb)
    debug("Warning: %s %s" % (warning, string.join(exception_log)))
    return "".join(exception_log)

t0 = None
def deltat():
    global t0
    t1 = time.time()
    if t0 is None:
        dt = 0
    else:
        dt = t1 - t0
    t0 = t1
    return dt

def trace(verbose=False):
    def _printtime(f):
        def new_f(*args, **kw):
            if verbose:
                print '--> %s %.2f' % (f.func_name, deltat())
                print args
                print kw
            else:
                deltat()
            result = f(*args, **kw)
            print '<-- %s %.2f' % (f.func_name, deltat())
            if verbose:
                print (result,)
            return result
        new_f.func_name = f.func_name
        return new_f
        
    return _printtime

def oslink(frompath, topath):
    if sys.platform == 'win32':
        win32file.CreateHardLink(topath, frompath, None)
    else:
        os.link(frompath, topath)

def utf8(str):
    return str.encode('utf-8', 'replace')

def unify(str, encoding=None):
    """Converts to unicode with warnings instead of tracebacks."""
    if isinstance(str, unicode):
        return str
    try:
        return unicode(str, encoding=encoding)
    except:
        helper.warning(
            'Cannot generate unicode for %s' % str)
        return unicode(str, encoding=encoding, errors='replace')

def makeDirectories(dir_path, permissions=0755):
    import os
    try :
        os.makedirs(dir_path, permissions)
    except OSError, err:
        # Reraise the error unless it's about an already existing directory
        # (see p. 143 of the Python Cookbook)
        if err.errno != errno.EEXIST or not os.path.isdir(dir_path):
            raise




