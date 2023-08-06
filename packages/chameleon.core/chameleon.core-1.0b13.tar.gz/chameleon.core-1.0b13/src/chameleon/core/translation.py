from StringIO import StringIO
from cPickle import dumps

import generation
import codegen
import clauses
import itertools
import types
import utils
import config
import etree
import marshal
import sys

GLOBALS = globals()

class Node(object):
    """Element translation class.

    This class implements the translation node for an element in the
    template document tree.

    It's used internally by the translation machinery.
    """

    symbols = config.SYMBOLS

    translate = None
    translation_name = None
    translation_domain = None
    translated_attributes = None
    skip = None
    cdata = None
    omit = None
    assign = None
    define = None
    macro = None
    use_macro = None
    define_macro = None
    fill_slot = None
    define_slot = None
    condition = None
    repeat = None
    content = None
    include = None
    format = None
    dict_attributes = None
    dynamic_attributes = utils.emptydict()

    ns_omit = "http://xml.zope.org/namespaces/meta",
    
    def __init__(self, element):
        self.element = element

    @property
    def tag(self):
        tag = self.element.tag
        if '}' in tag:
            url, tag = tag[1:].split('}')
            for prefix, _url in self.element.nsmap.items():
                if prefix is not None and _url == url:
                    return "%s:%s" % (prefix, tag)
        return tag
    
    @property
    def text(self):
        if self.element.text is None:
            return ()
        return (self.element.text,)

    @property
    def tail(self):
        if self.element.tail is None:
            return ()
        return (self.element.tail,)

    @property
    def ns_attributes(self):
        root = self.element.getroottree().getroot()
        if root is None or utils.get_namespace(root) == config.META_NS:
            return {}
        
        prefix_omit = set()
        namespaces = self.element.nsmap.values()

        parent = self.element.getparent()
        while parent is not None:
            for prefix, ns in parent.nsmap.items():
                if ns in namespaces:
                    prefix_omit.add(prefix)
            parent = parent.getparent()

        attrs = dict(
            ((prefix and "xmlns:%s" % prefix or "xmlns", ns) for (prefix, ns) in \
             self.element.nsmap.items() if \
             ns not in self.ns_omit and prefix not in prefix_omit))

        return attrs
    
    @property
    def static_attributes(self):
        result = {}

        for prefix, ns in self.element.nsmap.items():
            if ns not in self.ns_omit:
                attrs = utils.get_attributes_from_namespace(self.element, ns)
                attrs.update(
                    utils.get_attributes_from_namespace(self.element, None))
                    
                for tag, value in attrs.items():
                    name = tag.split('}')[-1]
                    
                    if prefix and self.element.prefix != prefix:
                        result["%s:%s" % (prefix, name)] = value
                    else:
                        result[name] = value

        if self.element.prefix is None:
            result.update(
                utils.get_attributes_from_namespace(self.element, None))

        return result

    @property
    def stream(self):
        return self.element.stream
    
    def update(self):
        self.element.update()
    
    def begin(self):
        self.stream.scope.append(set())
        self.stream.begin(self.serialize())
        
    def end(self):
        self.stream.end(self.serialize())
        self.stream.scope.pop()

    def body(self):
        if isinstance(self.skip, types.expression):
            assert isinstance(self.skip, types.value), \
                   "Dynamic skip condition can't be of type %s." % type(self.skip)
            condition = clauses.Condition(self.skip, invert=True)
            if len(self.element):
                condition.begin(self.stream)
        elif self.skip:
            return
        
        for element in self.element:
            element.node.update()

        for element in self.element:
            element.node.visit()

        if isinstance(self.skip, types.expression):
            if len(self.element):
                condition.end(self.stream)
                    
    def visit(self):
        assert self.stream is not None, "Must use ``start`` method."

        for element in self.element:
            if not isinstance(element, Element):
                self.wrap_literal(element)

        self.update()
        self.begin()
        self.body()
        self.end()

    def serialize(self):
        """Serialize element into clause-statements."""

        _ = []

        # i18n domain
        if self.translation_domain is not None:
            _.append(clauses.Define(
                self.symbols.domain, types.value(repr(self.translation_domain))))

        # variable definitions
        if self.define is not None:
            for declaration, expression in self.define:
                _.append(clauses.Define(
                    declaration, expression, self.symbols.scope))

        # tag tail (deferred)
        tail = self.tail
        if self.fill_slot is None and self.translation_name is None:
            for part in reversed(tail):
                if isinstance(part, types.expression):
                    _.append(clauses.Write(part, defer=True))
                else:
                    _.append(clauses.Out(part, defer=True))
            
        # macro method
        macro = self.macro
        if macro is not None:
            _.append(clauses.Method(
                macro.name, macro.args, decorators=macro.decorators))
                
        # condition
        if self.condition is not None:
            _.append(clauses.Condition(self.condition))

        # repeat
        if self.repeat is not None:
            variables, expression = self.repeat
            if len(variables) > 1:
                repeat = clauses.Repeat(variables, expression, repeatdict=False)
            else:
                repeat = clauses.Repeat(variables, expression)
            _.append(repeat)

        # assign
        if self.assign is not None:
            for declaration, expression in self.assign:
                if len(declaration) != 1:
                    raise ValueError("Can only assign single variable.")
                variable = declaration[0]
                _.append(clauses.Assign(
                    expression, variable))        

        content = self.content

        # macro slot definition
        if self.define_slot:
            # check if slot has been filled
            name = self.symbols.slot + utils.normalize_slot_name(self.define_slot)
            if name in itertools.chain(*self.stream.scope):
                _.append(clauses.Condition(
                    types.value('isinstance(%s, basestring)' % name),
                    (clauses.Assign(
                    types.value('%s(%s)' % (
                    name, self.symbols.scope)),
                    name),),
                    finalize=True,
                    invert=True))
                     
                content = types.value(name)

        # set dynamic content flag
        dynamic = content or self.translate is not None

        # static attributes are at the bottom of the food chain
        attributes = utils.odict()
        attributes.update(self.static_attributes)
        attributes.update(self.ns_attributes)

        # dynamic attributes
        dynamic_attrs = self.dynamic_attributes or ()
        dynamic_attr_names = []
        
        for variables, expression in dynamic_attrs:
            if len(variables) != 1:
                raise ValueError("Tuple definitions in assignment clause "
                                     "is not supported.")

            variable = variables[0]
            attributes[variable] = expression
            dynamic_attr_names.append(variable)

        # translated attributes
        translated_attributes = self.translated_attributes or ()
        for variable, msgid in translated_attributes:
            if msgid:
                if variable in dynamic_attr_names:
                    raise ValueError(
                        "Message id not allowed in conjunction with "
                        "a dynamic attribute.")

                value = types.value('"%s"' % msgid)

                if variable in attributes:
                    default = '"%s"' % attributes[variable]
                    expression = self.translate_expression(value, default=default)
                else:
                    expression = self.translate_expression(value)
            else:
                value = attributes.get(variable)
                if value is not None:
                    if variable not in dynamic_attr_names:
                        value = '"%s"' % value
                    expression = self.translate_expression(value)
                else:
                    raise ValueError("Must be either static or dynamic "
                                     "attribute when no message id "
                                     "is supplied.")

            attributes[variable] = expression

        # tag
        text = self.text
        if self.omit is not True:
            selfclosing = not text and not dynamic and len(self.element) == 0
            tag = clauses.Tag(
                self.tag, attributes,
                expression=self.dict_attributes, selfclosing=selfclosing,
                cdata=self.cdata is not None, defaults=self.static_attributes)
            if self.omit:
                _.append(clauses.Condition(
                    self.omit, [tag], finalize=False, invert=True))
            else:
                _.append(tag)

        # tag text (if we're not replacing tag body)
        if len(text) and not dynamic and not self.use_macro:
            for part in text:
                if isinstance(part, types.expression):
                    _.append(clauses.Write(part))
                else:
                    _.append(clauses.Out(part))

        # dynamic content
        if content:
            msgid = self.translate
            if msgid is not None:
                if msgid:
                    raise ValueError(
                        "Can't use message id with dynamic content translation.")

                _.append(clauses.Assign(content, self.symbols.tmp))
                content = self.translate_expression(
                    types.value(self.symbols.tmp))
                
            _.append(clauses.Write(content))

        # dynamic text
        elif self.translate is not None and \
                 True in map(lambda part: isinstance(part, types.expression), text):
            if len(self.element):
                raise ValueError(
                    "Can't translate dynamic text block with elements in it.")

            init_stream = types.value('_init_stream()')
            init_stream.symbol_mapping['_init_stream'] = generation.initialize_stream
            
            subclauses = []
            subclauses.append(clauses.Define(
                types.declaration((self.symbols.out, self.symbols.write)), init_stream))

            for part in text:
                if isinstance(part, types.expression):
                    subclauses.append(clauses.Write(part))
                else:
                    part = part.strip().replace('  ', ' ').replace('\n', '')
                    if part != "":
                        subclauses.append(clauses.Out(part))

            # attempt translation
            subclauses.append(clauses.Assign(
                self.translate_expression(
                types.value('%(out)s.getvalue()'), 
                default=None), self.symbols.tmp))

            _.append(clauses.Group(subclauses))
            _.append(clauses.Write(types.value(self.symbols.tmp)))

        # include
        elif self.include:
            # compute macro function arguments and create argument string
            arguments = [
                "%s=%s" % (arg, arg) for arg in \
                 set(itertools.chain(*self.stream.scope))]

            # XInclude's are similar to METAL macros, except the macro
            # is always defined as the entire template.

            # first we compute the filename expression and write it to
            # an internal variable
            _.append(clauses.Assign(self.include, self.symbols.include))

            # call template
            _.append(clauses.Write(
                types.template(
                "%%(xincludes)s.get(%%(include)s, %s).render_xinclude(%s)" % \
                (repr(self.format), ", ".join(arguments)))))
            
        # use macro
        elif self.use_macro:
            # for each fill-slot element, create a new output stream
            # and save value in a temporary variable
            kwargs = []
            for element in etree.elements_with_attribute(
                self.element, config.METAL_NS, 'fill-slot'):
                if element.node.fill_slot is None:
                    # XXX this should not be necessary, but the above
                    # xpath expression finds non-"metal:fill-slot"
                    # nodes somehow on my system; this is perhaps due
                    # to a bug in the libxml2 version I'm using; we
                    # work around it by just skipping the element.
                    # (chrism)
                    continue

                callback = self.symbols.slot + \
                           utils.normalize_slot_name(element.node.fill_slot)
                remote_scope = self.symbols.scope+"_remote"
                kwargs.append((callback, callback))

                scope_args = tuple(
                    "%s=%s" % (variable, variable) for variable in \
                    set(itertools.chain(*self.stream.scope)))

                init_stream = types.value('_init_stream()')
                init_stream.symbol_mapping['_init_stream'] = generation.initialize_stream

                subclauses = []
                subclauses.append(
                    clauses.Method(
                    callback, (
                    remote_scope,) + scope_args,
                    types.value('%s.getvalue()' % self.symbols.out)))
                subclauses.append(
                    clauses.UpdateScope(self.symbols.scope, remote_scope))
                subclauses.append(clauses.Assign(
                    init_stream, (self.symbols.out, self.symbols.write)))
                subclauses.append(clauses.Visit(element.node))
                _.append(clauses.Group(subclauses))

            _.append(clauses.Assign(self.use_macro, self.symbols.metal))

            # compute macro function arguments and create argument string
            if 'xmlns' in self.element.attrib:
                kwargs.append(('include_ns_attribute', repr(True)))

            arguments = tuple("%s=%s" % (arg, arg) for arg in \
                              itertools.chain(*self.stream.scope))+ \
                        tuple("%s=%s" % kwarg for kwarg in kwargs)
            arguments = ", ".join(set(arguments))

            value = types.value(
                "%s.render(%s)" % (self.symbols.metal, arguments))
            value.label = self.use_macro.label
            _.append(clauses.Write(value))

        # translate body
        elif self.translate is not None:
            msgid = self.translate
            if not msgid:
                msgid = self.create_msgid()

            # for each named block, create a new output stream
            # and use the value in the translation mapping dict
            elements = [e for e in self.element if e.node.translation_name]

            if elements:
                mapping = self.symbols.mapping
                _.append(clauses.Assign(types.value('{}'), mapping))
            else:
                mapping = 'None'

            for element in elements:
                name = element.node.translation_name

                init_stream = types.value('_init_stream()')
                init_stream.symbol_mapping['_init_stream'] = generation.initialize_stream

                subclauses = []
                subclauses.append(clauses.Define(
                    types.declaration((self.symbols.out, self.symbols.write)), init_stream))
                subclauses.append(clauses.Visit(element.node))
                subclauses.append(clauses.Assign(
                    types.template('%(out)s.getvalue()'),
                    "%s['%s']" % (mapping, name)))

                _.append(clauses.Group(subclauses))

            _.append(clauses.Assign(
                self.translate_expression(
                types.value(repr(msgid)), mapping=mapping,
                default=self.symbols.marker), self.symbols.result))

            # write translation to output if successful, otherwise
            # fallback to default rendition; 
            result = types.value(self.symbols.result)
            result.symbol_mapping[self.symbols.marker] = generation.marker
            condition = types.template('%(result)s is not %(marker)s')
            _.append(clauses.Condition(
                condition, [clauses.UnicodeWrite(result)], finalize=True))

            subclauses = []
            if self.element.text:
                subclauses.append(clauses.Out(self.element.text))
            for element in self.element:
                name = element.node.translation_name
                if name:
                    value = types.value("%s['%s']" % (mapping, name))
                    subclauses.append(clauses.Write(value))
                else:
                    subclauses.append(clauses.Out(utils.serialize(element)))
                    
                for part in reversed(element.node.tail):
                    if isinstance(part, types.expression):
                        subclauses.append(clauses.Write(part))
                    else:
                        subclauses.append(clauses.Out(part))
                    
            if subclauses:
                _.append(clauses.Else(subclauses))

        return _

    def wrap_literal(self, element):
        index = self.element.index(element)

        t = self.element.makeelement(utils.meta_attr('literal'))
        t.meta_omit = ""
        t.tail = element.tail
        t.text = unicode(element)
        for child in element.getchildren():
            t.append(child)
        self.element.remove(element)
        self.element.insert(index, t)
        t.update()

    def create_msgid(self):
        """Create an i18n msgid from the tag contents."""

        out = StringIO()
        out.write(self.element.text)
        
        for element in self.element:
            name = element.node.translation_name
            if name:
                out.write("${%s}" % name)
                out.write(element.tail)
            else:
                out.write(element.tostring())

        msgid = out.getvalue().strip()
        msgid = msgid.replace('  ', ' ').replace('\n', '')

        return msgid

    def translate_expression(self, value, mapping=None, default=None):
        format = "%%(translate)s(%s, domain=%%(domain)s, mapping=%s, " \
                 "target_language=%%(language)s, default=%s)"
        template = types.template(
            format % (value, mapping, default))

        # add translate-method to symbol mapping
        translate = generation.fast_translate
        template.symbol_mapping[config.SYMBOLS.translate] = translate

        return template
    
class Element(etree.ElementBase):
    """Template element class.

    To start translation at this element, use the ``start`` method,
    providing a code stream object.
    """

    translator = None
    
    class node(Node):
        @property
        def omit(self):
            if self.element.meta_omit is not None:
                return self.element.meta_omit or True
            if self.element.meta_replace:
                return True

        @property
        def content(self):
            return self.element.meta_replace

    node = property(node)
    
    def start(self, stream):
        self._stream = stream
        self.node.visit()

    def update(self):
        pass
    
    @property
    def stream(self):
        while self is not None:
            try:
                return self._stream
            except AttributeError:
                self = self.getparent()

        raise ValueError("Can't locate stream object.")

    meta_cdata = etree.Annotation(
        utils.meta_attr('cdata'))
    
    meta_omit = etree.Annotation(
        utils.meta_attr('omit-tag'))
    
    meta_attributes = etree.Annotation(
        utils.meta_attr('attributes'))

    meta_replace = etree.Annotation(
        utils.meta_attr('replace'))

class MetaElement(Element):
    meta_cdata = etree.Annotation('cdata')
    
    meta_omit = True

    meta_attributes = etree.Annotation('attributes')

    meta_replace = etree.Annotation('replace')

class Compiler(object):
    """Template compiler. ``implicit_doctype`` will be used as the
    document type if the template does not define one
    itself. ``explicit_doctype`` may be used to explicitly set a
    doctype regardless of what the template defines."""

    doctype = None
    xml_declaration = None
        
    def __init__(self, body, parser, explicit_doctype=None, encoding=None):
        self.tree = parser.parse(body)
        self.parser = parser

        # it's not clear from the tree if an XML declaration was
        # present in the document source; the following is a
        # work-around to ensure that output matches input
        if '<?xml ' in body:
            self.xml_declaration = \
            """<?xml version="%s" encoding="%s" standalone="no" ?>""" % (
                self.tree.docinfo.xml_version, self.tree.docinfo.encoding)
            
        # explicit document type has priority over a parsed doctype
        if explicit_doctype is not None:
            self.doctype = explicit_doctype
        elif self.tree.docinfo.doctype:
            self.doctype = self.tree.docinfo.doctype
        
        if utils.coerces_gracefully(encoding):
            self.encoding = None
        else:
            self.encoding = encoding
        
    @classmethod
    def from_text(cls, body, parser, **kwargs):
        compiler = Compiler(
            "<html xmlns='%s'></html>" % config.XHTML_NS, parser,
            encoding=kwargs.get('encoding'))
        root = compiler.tree.getroot()
        root.text = body
        root.meta_omit = ""
        return compiler

    def __call__(self, macro=None, global_scope=True, parameters=()):
        root = self.tree.getroot()

        if not isinstance(root, Element):
            raise ValueError(
                "Must define valid namespace for tag: '%s.'" % root.tag)

        # if macro is non-trivial, start compilation at the element
        # where the macro is defined
        if macro:
            elements = tuple(etree.elements_with_attribute(
                root, config.METAL_NS, 'define-macro', macro))

            if not elements:
                raise ValueError("Macro not found: %s." % macro)

            element = elements[0]
            element.meta_translator = root.meta_translator

            # if element is the document root, render as a normal
            # template, e.g. unset the `macro` mode
            if root is element:
                macro = None
            else:
                root = element

            # remove macro definition attribute from element
            if element.nsmap.get(element.prefix) == config.METAL_NS:
                del element.attrib['define-macro']
            else:
                del element.attrib[utils.metal_attr('define-macro')]

        # initialize code stream object
        stream = generation.CodeIO(
            root.node.symbols, encoding=self.encoding,
            indentation=0, indentation_string="\t")

        # initialize variable scope
        stream.scope.append(set(
            (stream.symbols.out,
             stream.symbols.write,
             stream.symbols.scope,
             stream.symbols.domain,
             stream.symbols.language) + \
            tuple(parameters)))

        # set up initialization code
        stream.symbol_mapping['_init_stream'] = generation.initialize_stream
        stream.symbol_mapping['_init_scope'] = generation.initialize_scope
        stream.symbol_mapping['_init_tal'] = generation.initialize_tal

        # add code-generation lookup globals
        stream.symbol_mapping.update(codegen.lookup_globals)
        
        if global_scope:
            assignments = (
                clauses.Assign(
                     types.value("_init_stream()"), ("%(out)s", "%(write)s")),
                clauses.Assign(
                     types.value("_init_scope()"), "%(scope)s"),
                clauses.Assign(
                     types.value("_init_tal()"), ("%(attributes)s", "%(repeat)s")),
                clauses.Assign(
                     types.template("None"), "%(domain)s"))
        else:
            assignments = (
                clauses.Assign(
                    types.value("_init_tal()"), ("%(attributes)s", "%(repeat)s")),
                clauses.Assign(
                     types.template("None"), "%(domain)s"))
                
        for clause in assignments:
            clause.begin(stream)
            clause.end(stream)

        if macro is not None:
            if macro == "" and 'xmlns' in root.attrib:
                del root.attrib['xmlns']

            wrapper = self.tree.parser.makeelement(
                utils.meta_attr('wrapper'), root.attrib)
            wrapper.append(root)
            root = wrapper
            
        # output XML headers, if applicable
        if not macro:
            header = ""
            if self.xml_declaration is not None:
                header += self.xml_declaration + '\n'
            if self.doctype:
                doctype = self.doctype + '\n'
                if self.encoding:
                    doctype = doctype.encode(self.encoding)
                header += doctype
            if header:
                out = clauses.Out(header)
                stream.scope.append(set())
                stream.begin([out])
                stream.end([out])
                stream.scope.pop()

        # start generation
        root.start(stream)
        body = stream.getvalue()

        # symbols dictionary
        __dict__ = stream.symbols.__dict__

        # prepare args
        args = list(parameters)

        # prepare kwargs
        defaults = ["%s = None" % param for param in parameters]

        if not stream.symbols.language in args:
            args.append('%(language)s = None' % __dict__)

        # prepare globals
        _globals = ["from cPickle import loads as _loads"]
        for symbol, value in stream.symbol_mapping.items():
            _globals.append(
                "%s = _loads(%s)" % (symbol, repr(dumps(value))))
            
        # wrap generated Python-code in function definition
        if global_scope:
            source = generation.function_wrap(
                'render', args, _globals, body,
                "%(out)s.getvalue()" % stream.symbols.__dict__)
        else:
            source = generation.function_wrap(
                'render', defaults, _globals, body)

        return ByteCodeTemplate(source)

class ByteCodeTemplate(object):
    """Template compiled to byte-code."""

    func = None
    
    def __init__(self, source):
        self.source = source

    def compile(self):
        suite = codegen.Suite(self.source)        
        _locals = {}
        exec suite.source in _locals
        self.bind = _locals['bind']
        self.func = self.bind()
        self.source = suite.source
        
    def __reduce__(self):
        reconstructor, (cls, base, state), kwargs = \
                       GhostedByteCodeTemplate(self).__reduce__()
        return reconstructor, (ByteCodeTemplate, base, state), kwargs

    def __setstate__(self, state):
        self.__dict__.update(GhostedByteCodeTemplate.rebuild(state))

    @property
    def render(self):
        return self.func

class GhostedByteCodeTemplate(object):
    def __init__(self, template):
        self.code = marshal.dumps(template.bind.func_code)
        self.defaults = len(template.bind.func_defaults or ())
        self.source = template.source
        
    @classmethod
    def rebuild(cls, state):
        source = state['source']

        bind = sys.modules['types'].FunctionType(
            marshal.loads(state['code']), GLOBALS, "bind")

        func = bind()
        
        return dict(
            bind=bind,
            func=func,
            source=source)
            
