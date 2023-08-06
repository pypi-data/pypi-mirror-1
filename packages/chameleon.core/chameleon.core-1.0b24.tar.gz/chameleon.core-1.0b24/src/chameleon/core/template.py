import os
import sys
import etree
import utils
import config
import filecache
import translation

class Template(object):
    """Constructs a template object using the template language
    defined by ``parser`` (``ZopePageTemplateParser`` or
    ``GenshiParser`` as of this writing). Must be passed an input
    string as ``body``. The ``format`` parameter supports values 'xml'
    and 'text'. Pass a value for ``encoding`` if you need to allow
    strings that are not unicode or plain ASCII."""

    format = 'xml'
    version = 3
    filename = '<string>'

    explicit_doctype = None
    
    def __init__(self, body, parser, format=None, doctype=None, encoding=None):
        self.parser = parser        
        self.encoding = encoding
        self.signature = hash(body)
        self.registry = {}
        
        if format is not None:
            self.format = format

        if doctype is not None:            
            self.explicit_doctype = doctype

        self.body = body

    def __repr__(self):
        return u"<%s %s>" % (self.__class__.__name__, self.filename)

    def __call__(self, **kwargs):
        return self.render(**kwargs)

    def write(self, body):
        self.__dict__['body'] = body
        self.__dict__.pop('compiler', None)
        if config.EAGER_PARSING:
            self.parse()
        
    def parse(self):
        body = self.__dict__['body']
        
        # if the body is trivial, we don't try to compile it
        if None in (body, self.parser):
            return
        
        parse_method = getattr(self.parser, 'parse_%s' % self.format)

        try:
            tree = parse_method(body)
        except:
            utils.raise_template_exception(
                "", repr(self), {}, sys.exc_info())

        # it's not clear from the tree if an XML declaration was
        # present in the document source; the following is a
        # work-around to ensure that output matches input
        if '<?xml ' in body:
            xml_declaration = \
            """<?xml version="%s" encoding="%s" standalone="no" ?>""" % (
                tree.docinfo.xml_version, tree.docinfo.encoding)
        else:
            xml_declaration = None

        compiler = self.__dict__['compiler'] = translation.Compiler(
            tree, explicit_doctype=self.explicit_doctype,
            xml_declaration=xml_declaration, encoding=self.encoding)

        return compiler
    
    @property
    def compiler(self):
        try:
            return self.__dict__['compiler']
        except KeyError:
            return self.parse()

    body = property(lambda template: template.__dict__['body'], write)
    
    @property
    def macros(self):
        return Macros(self.render_macro, *self.compiler.macros)

    def cook(self, **kwargs):
        template = self.compiler(**kwargs)
        template.compile()
        return template
    
    def cook_check(self, parameters, **kwargs):
        assert self.compiler is not None
        key = tuple(parameters), \
              tuple(item for item in kwargs.iteritems()), \
              self.signature, self.explicit_doctype
        template = self.registry.get(key, None)
        if template is None:
            template = self.cook(parameters=parameters, **kwargs)
            self.registry[key] = template
        return template

    def render(self, **kwargs):
        template = self.cook_check(parameters=kwargs)
        return self.render_template(template, **kwargs)

    def render_macro(self, macro, global_scope=False, parameters={}):
        template = self.cook_check(
            parameters=parameters, macro=macro, global_scope=global_scope)
        return self.render_template(template, **parameters)
    
    def render_xinclude(self, **kwargs):
        return self.render_macro("", parameters=kwargs)

    def render_template(self, __template__, **kwargs):
        __traceback_info__ = (self,)
        if config.DEBUG_MODE is False:
            return __template__.render(**kwargs)
        
        try:
            return __template__.render(**kwargs)
        except:
            utils.raise_template_exception(
                __template__.source, repr(self), kwargs, sys.exc_info())

class TemplateFile(Template):
    """Constructs a template object using the template language
    defined by ``parser``. Must be passed an absolute (or
    current-working-directory-relative) filename as ``filename``. If
    ``auto_reload`` is true, each time the template is rendered, it
    will be recompiled if it has been changed since the last
    rendering."""
    
    global_registry = {}

    def __init__(self, filename, parser, format=None,  doctype=None,
                 auto_reload=config.DEBUG_MODE):
        Template.__init__(
            self, None, parser, format=format, doctype=doctype)

        self.auto_reload = auto_reload
        self.filename = filename = os.path.abspath(
            os.path.normpath(os.path.expanduser(filename)))

        # make sure file exists
        os.lstat(filename)

        # read template
        self.read()

        # persist template registry on disk
        if config.DISK_CACHE:
            version = ".".join(
                map(str, (getattr(base, 'version', 0) for \
                    base in type(self).__bases__)))
            self.registry = filecache.TemplateCache(filename, version)

        self.global_registry.setdefault(filename, self)
        self.xincludes = XIncludes(
            self.global_registry, os.path.dirname(filename), self.clone)
        
    def clone(self, filename, format=None):
        cls = type(self)
        return cls(
            filename, self.parser, format=format,
            doctype=self.explicit_doctype, auto_reload=self.auto_reload)
        
    def _get_filename(self):
        return getattr(self, '_filename', None)

    def _set_filename(self, filename):
        self._filename = filename
        self._v_last_read = False

    filename = property(_get_filename, _set_filename)

    def read(self):
        filename = self.filename
        mtime = self.mtime()
        fd = open(filename, 'r')
        self.body = body = fd.read()
        fd.close()
        self.signature = filename, mtime
        self._v_last_read = mtime
        
    def cook(self, **kwargs):
        try:
            template = self.compiler(**kwargs)
        except (SyntaxError, etree.XMLSyntaxError), exception:
            exception.msg += ' (%s)' % self.filename
            raise exception

        try:
            template.compile()
        finally:
            if config.DEBUG_SOURCE:
                filename = "%s.py" % self.filename
                f = open(filename, 'w')
                f.write(template.source)
                f.close()

        return template

    @property
    def compiler(self):
        if self.auto_reload and self._v_last_read != self.mtime():
            self.read()
        try:
            return self.__dict__['compiler']
        except KeyError:
            return self.parse()

    def render(self, **kwargs):
        kwargs[config.SYMBOLS.xincludes] = self.xincludes
        return super(TemplateFile, self).render(**kwargs)

    def mtime(self):
        try:
            return os.path.getmtime(self.filename)
        except (IOError, OSError):
            return 0

class XIncludes(object):
    """Dynamic XInclude registry providing a ``get``-method that will
    resolve a filename to a template instance. Format must be
    explicitly provided."""
    
    def __init__(self, registry, relpath, factory):
        self.registry = registry
        self.relpath = relpath
        self.factory = factory

    def get(self, filename, format):
        if not os.path.isabs(filename):
            filename = os.path.join(self.relpath, filename)        
        template = self.registry.get(filename)
        if template is not None:
            return template
        return self.factory(filename, format=format)
    
class Macro(object):
    def __init__(self, render):
        self.render = render

class Macros(object):
    def __init__(self, render_macro, *names, **kwargs):
        self.render = render_macro
        self.bound_parameters = kwargs
        self.names = names
        
    def __getitem__(self, name):
        if name and name not in self.names:
            raise KeyError(name)
        return self.get_macro(name)

    def get_macro(self, name):
        def render(**kwargs):
            kwargs.update(self.bound_parameters)
            return self.render(name, parameters=kwargs)
        return Macro(render)

    def bind(self, **kwargs):
        return Macros(self.render, *self.names, **kwargs)
