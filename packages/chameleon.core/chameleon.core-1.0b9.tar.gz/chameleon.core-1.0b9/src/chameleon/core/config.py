import os

# define which values are read as true
TRUEVALS = ('y', 'yes', 't', 'true', 'on', '1')

# in debug-mode, templates on disk are reloaded if they're modified
DEBUG_MODE_KEY = 'CHAMELEON_DEBUG'
DEBUG_MODE = os.environ.get(DEBUG_MODE_KEY, 'false')
DEBUG_MODE = DEBUG_MODE.lower() in TRUEVALS

# disable disk-cache to prevent the compiler from caching on disk
DISK_CACHE_KEY = 'CHAMELEON_CACHE'
DISK_CACHE = os.environ.get(DISK_CACHE_KEY, 'true')
DISK_CACHE = DISK_CACHE.lower() in TRUEVALS
CACHE_EXTENSION = "cache"

# when validation is enabled, dynamically inserted content is
# validated against the XHTML standard
VALIDATION_KEY = 'CHAMELEON_VALIDATE'
VALIDATION = os.environ.get(VALIDATION_KEY, 'false')
VALIDATION = VALIDATION.lower() in TRUEVALS

# these definitions are standard---change at your own risk!
XHTML_NS = "http://www.w3.org/1999/xhtml"
TAL_NS = "http://xml.zope.org/namespaces/tal"
META_NS = "http://xml.zope.org/namespaces/meta"
METAL_NS = "http://xml.zope.org/namespaces/metal"
XI_NS = "http://www.w3.org/2001/XInclude"
I18N_NS = "http://xml.zope.org/namespaces/i18n"
PY_NS = "http://genshi.edgewall.org/"
NS_MAP = dict(py=PY_NS, tal=TAL_NS, metal=METAL_NS)

# the symbols table below is used internally be the compiler
class SYMBOLS(object):
    # internal use only
    init = '_init'
    slot = '_slot'
    metal = '_metal'
    include = '_include'
    macro = '_macro'
    out = '_out'
    tmp = '_tmp'
    write = '_write'
    mapping = '_mapping'
    result = '_result'
    marker = '_marker'
    domain = '_domain'
    i18n_context = '_i18n_context'
    attributes = '_attributes'
    negotiate = '_negotiate'
    translate = '_translate'
    validate = '_validate'
    
    # advertised symbols
    repeat = 'repeat'
    language = 'target_language'
    xincludes = 'xincludes'
    default = 'default'
    scope = 'econtext'

    @classmethod
    def as_dict(cls):
        return dict((name, getattr(cls, name)) for name in dir(cls))
            
