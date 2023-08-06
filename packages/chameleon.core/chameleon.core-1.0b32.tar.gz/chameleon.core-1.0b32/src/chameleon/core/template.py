import os
import sys
import doctypes
import utils
import config
import filecache
import translation
import xml.parsers.expat

class Template(object):
    """Constructs a template object using the template language
    defined by ``parser`` (``ZopePageTemplateParser`` or
    ``GenshiParser`` as of this writing). Must be passed an input
    string as ``body``. The ``format`` parameter supports values 'xml'
    and 'text'. Pass a value for ``encoding`` if you need to allow
    strings that are not unicode or plain ASCII."""

    format = 'xml'
    version = 5
    filename = '<string>'
    explicit_doctype = None
    
    def __init__(self, body, parser, format=None,
                 doctype=None, encoding=None, omit_default_prefix=True):
        self.parser = parser        
        self.encoding = encoding
        self.signature = hash(body)
        self.registry = {}
        
        if format is not None:
            self.format = format

        if doctype is not None:            
            self.explicit_doctype = doctype

        self.body = body
        self.omit_default_prefix = omit_default_prefix
        
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

        explicit_doctype = self.explicit_doctype
        if not explicit_doctype is doctypes.no_doctype and not explicit_doctype:
            explicit_doctype = self.parser.doctype

        compiler = translation.Compiler(
            tree, explicit_doctype=explicit_doctype,
            xml_declaration=xml_declaration, encoding=self.encoding,
            omit_default_prefix=self.omit_default_prefix)
        macros = Macros(self.render_macro, *compiler.macros)

        self.__dict__['compiler'] = compiler
        self.__dict__['macros'] = macros
        
        return compiler
    
    @property
    def compiler(self):
        try:
            return self.__dict__['compiler']
        except KeyError:
            return self.parse()

    @property
    def macros(self):
        assert self.compiler is not None
        return self.__dict__['macros']

    body = property(lambda template: template.__dict__['body'], write)
    
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
    
    content_type = None
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

        __traceback_info__ = filename
        fd = open(filename, "rb")
        try:
            body = fd.read(utils.XML_PREFIX_MAX_LENGTH)
        except:
            fd.close()
            raise

        content_type = utils.sniff_type(body)
        if content_type == "text/xml":
            body += fd.read()
            fd.close()
        else:
            # For HTML, we really want the file read in text mode:
            fd.close()
            fd = open(filename)
            body = fd.read()
            fd.close()

            # Look for an encoding specification in the meta tag
            match = utils.re_meta.search(body)
            if match is not None:
                content_type, encoding = match.groups()
                # TODO: Shouldn't <meta>/<?xml?> stripping
                # be in PageTemplate.__call__()?
                body = utils.re_meta.sub("", body)
            else:
                content_type = None
                encoding = config.DEFAULT_ENCODING
            body = unicode(body, encoding).encode(config.DEFAULT_ENCODING)

        self.body = body
        self.content_type = content_type
        self.signature = filename, mtime
        self._v_last_read = mtime

    def cook(self, **kwargs):
        try:
            template = self.compiler(**kwargs)
        except (SyntaxError, xml.parsers.expat.ExpatError), exception:
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
