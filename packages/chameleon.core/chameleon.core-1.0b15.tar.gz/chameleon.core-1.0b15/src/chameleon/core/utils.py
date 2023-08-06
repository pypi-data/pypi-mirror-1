from zope import interface

import sys
import pprint
import config
import interfaces
import htmlentitydefs
import re

types = sys.modules['types']

from UserDict import UserDict

# check if we're able to coerce unicode to str
try:
    str(u'La Pe\xf1a')
    unicode_required_flag = False
except UnicodeEncodeError:
    unicode_required_flag = True

def coerces_gracefully(encoding):
    if encoding != sys.getdefaultencoding() and unicode_required_flag:
        return False
    return True

entities = "".join((
    '<!ENTITY %s "&#%s;">' % (name, text) for (name, text) in \
    htmlentitydefs.name2codepoint.items()))

re_annotation = re.compile(r'^\s*u?[\'"](.*)[\'"]$')

s_counter = 0
marker = object()

def handler(key=None):
    def decorate(f):
        def g(node):
            if key is None:
                return f(node, None)
            return f(node, node.get(key))
        g.__ns__ = key
        return g
    return decorate

def attribute(tokens, factory=None, default=None, encoding=None):
    def get(self):
        for token in isinstance(tokens, tuple) and tokens or (tokens,):
            value = self.attrib.get(token)
            if value is not None:
                if encoding or self.stream.encoding:
                    value = value.encode(encoding or self.stream.encoding)
                if factory is None:
                    return value
                f = factory(self.translator)
                return f(value)

        if default is not None:
            return default
    
    return property(get)

def escape(string, quote=None, encoding=None):
    if not isinstance(string, unicode) and encoding:
        string = string.decode(encoding)
    else:
        encoding = None

    table = htmlentitydefs.codepoint2name
    def get(char):
        key = ord(char)
        if key in table:
            return '&%s;' % table[key]
        return char
    
    string = "".join(map(get, string))

    if quote is not None:
        string = string.replace(quote, '\\'+quote)

    if encoding:
        string = string.encode(encoding)
        
    return string

re_normalize = re.compile(r'(^[0-9]|\b[^A-Za-z])')
def normalize_slot_name(name):
    return re_normalize.sub('_', name)
    
def serialize(element, encoding=None):
    return "".join(serialize_element(element, encoding))

def serialize_element(element, encoding):
    try:
        name = element.tag.split('}')[-1]
    except AttributeError:
        yield element.text; return
    
    # tag opening
    yield "<%s" % name

    # attributes
    for key, value in element.attrib.items():
        yield ' %s="%s"' % (key, escape('"', encoding=encoding))

    # elements with no text which have no children are self-closing.
    if element.text is None and len(element) == 0:
        yield ' />'; return

    yield '>'
            
    if element.text is not None:
        yield element.text

    for child in element:
        for string in serialize_element(child, encoding):
            yield string

    yield '</%s>' % name

class econtext(dict):
    """Dynamic scope dictionary which is compatible with the
    `econtext` of ZPT."""
    
    set_local = setLocal = dict.__setitem__
    set_global = setGlobal = dict.__setitem__

    @property
    def vars(self):
        return self
    
class scope(list):
    def __init__(self, *args):
        global s_counter
        self.hash = s_counter
        s_counter += 1

    def __hash__(self):
        return self.hash

class emptydict(dict):
    def __setitem__(self, key, value):
        raise TypeError("Read-only dictionary does not support assignment.")
    
class repeatitem(object):
    interface.implements(interfaces.ITALESIterator)
    
    def __init__(self, iterator, length):
        self.length = length
        self.iterator = iterator
        
    @property
    def index(self):
        try:
            length = len(self.iterator)
        except TypeError:
            length = self.iterator.__length_hint__()
        except:
            raise TypeError("Unable to determine length.")

        try:
            return self.length - length - 1
        except TypeError:
            return None
            
    @property
    def start(self):
        return self.index == 0

    @property
    def end(self):
        return self.index == self.length - 1

    def number(self):
        return self.index + 1

    def odd(self):
        return bool(self.index % 2)

    def even(self):
        return not self.odd()

class repeatdict(dict):
    def insert(self, key, iterable):
        """We realize the iterable and extract a new iterable from it;
        this allows us to keep track of the iteration and make
        available the repeat dictionary."""

        if not isinstance(iterable, (tuple, list)):
            try:
                iterable = tuple(iterable)
            except:
                # The message below to the TypeError is the Python
                # 2.5-style exception message. Python 2.4.X also
                # raises a TypeError, but with a different message.
                # ("TypeError: iteration over non-sequence").  The
                # Python 2.5 error message is more helpful.  We
                # construct the 2.5-style message explicitly here so
                # that both Python 2.4.X and Python 2.5+ will raise
                # the same error.  This makes writing the tests eaiser
                # and makes the output easier to understand.
                raise TypeError("%r object is not iterable" %
                                type(iterable).__name__)
            
        iterator = iter(iterable)
        length = len(iterable)
        self[key] = (iterator, length)
        
        return iterator
        
    def __getitem__(self, key):
        value, length = dict.__getitem__(self, key)

        if not isinstance(value, repeatitem):
            value = repeatitem(value, length)
            self[key] = (value, length)
            
        return value

class odict(UserDict):
    def __init__(self, dict = None):
        self._keys = []
        UserDict.__init__(self, dict)

    def __delitem__(self, key):
        UserDict.__delitem__(self, key)
        self._keys.remove(key)

    def __setitem__(self, key, item):
        """Case insensitive set item."""
        
        keys = tuple(key.lower() for key in self._keys)
        _key = key.lower()
        if _key in keys:
            for k in self._keys:
                if k.lower() == _key:
                    self._keys.remove(k)
                    key = k
                    break
                
        UserDict.__setitem__(self, key, item)
        self._keys.append(key)

    def clear(self):
        UserDict.clear(self)
        self._keys = []

    def copy(self):
        dict = UserDict.copy(self)
        dict._keys = self._keys[:]
        return dict

    def items(self):
        return zip(self._keys, self.values())

    def keys(self):
        return self._keys

    def popitem(self):
        try:
            key = self._keys[-1]
        except IndexError:
            raise KeyError('dictionary is empty')

        val = self[key]
        del self[key]

        return (key, val)

    def setdefault(self, key, failobj = None):
        UserDict.setdefault(self, key, failobj)
        if key not in self._keys: self._keys.append(key)

    def update(self, dict):
        UserDict.update(self, dict)
        for key in dict.keys():
            if key not in self._keys: self._keys.append(key)

    def values(self):
        return map(self.get, self._keys)
    
def get_attributes_from_namespace(element, namespace):
    if namespace is None:
        attrs = dict([
            (name, value) for (name, value) in element.attrib.items() \
            if '{' not in name])
    else:
        attrs = dict([
            (name, value) for (name, value) in element.attrib.items() \
            if name.startswith('{%s}' % namespace)])

    return attrs

def get_namespace(element):
    if '}' in element.tag:
        return element.tag.split('}')[0][1:]
    return element.nsmap.get(None)

def xhtml_attr(name):
    return "{%s}%s" % (config.XHTML_NS, name)

def tal_attr(name):
    return "{%s}%s" % (config.TAL_NS, name)

def meta_attr(name):
    return "{%s}%s" % (config.META_NS, name)

def metal_attr(name):
    return "{%s}%s" % (config.METAL_NS, name)

def i18n_attr(name):
    return "{%s}%s" % (config.I18N_NS, name)

def py_attr(name):
    return "{%s}%s" % (config.PY_NS, name)

def raise_template_exception(source, description, kwargs, exc_info):
    """Re-raise exception raised while calling ``template``, given by
    the ``exc_info`` tuple (see ``sys.exc_info``)."""

    # omit keyword arguments that begin with an underscore; these are
    # used internally be the template engine and should not be exposed
    kwargs = kwargs.copy()
    map(kwargs.__delitem__, [k for k in kwargs if k.startswith('_')])

    # format keyword arguments; consecutive arguments are indented for
    # readability
    formatted_arguments = pprint.pformat(kwargs).split('\n')
    for index, string in enumerate(formatted_arguments[1:]):
        formatted_arguments[index+1] = " "*15 + string

    # extract line number from traceback object
    cls, exc, tb = exc_info
    try:
        lineno = tb.tb_next.tb_lineno-1
    except AttributeError:
        lineno = 1
        
    # locate source code annotation (these are available from
    # the template source as comments)
    source = source.split('\n')
    for i in reversed(range(lineno)):
        m = re_annotation.match(source[i])
        if m is not None:
            annotation = m.group(1)
            break
    else:
        annotation = ""

    error_msg = (
        "Caught exception rendering template."
        "\n\n"
        " - Expression: \"%s\"\n"
        " - Instance:   %s\n"
        " - Arguments:  %s\n"
        ) % (annotation, description, "\n".join(formatted_arguments))    

    __dict__ = exc.__dict__
    __name__ = cls.__name__
    
    error_string = str(exc)
        
    if issubclass(cls, Exception):
        class RuntimeError(cls):
            def __init__(self, *args, **kwargs):
                pass
            
            def __str__(self):
                return "%s\n%s: %s" % (
                    error_msg, __name__, error_string)

        if isinstance(cls, types.TypeType):
            exc = RuntimeError.__new__(RuntimeError)
            exc.__dict__.update(__dict__)
        else:
            cls = RuntimeError
            
    raise cls, exc, tb
