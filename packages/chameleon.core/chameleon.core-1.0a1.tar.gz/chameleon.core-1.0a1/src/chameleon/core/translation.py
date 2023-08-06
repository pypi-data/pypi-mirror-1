from StringIO import StringIO

import generation
import codegen
import clauses
import doctypes
import itertools
import types
import utils
import config
import etree
import marshal
import htmlentitydefs

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
    static_attributes = utils.emptydict()
    dynamic_attributes = utils.emptydict()
    
    def __init__(self, element):
        self.element = element

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
        if not self.skip:
            for element in self.element:
                element.node.update()

            for element in self.element:
                element.node.visit()
                    
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
                if declaration.global_scope:
                    _.append(clauses.Define(
                        declaration, expression, self.symbols.scope))
                else:
                    _.append(clauses.Define(declaration, expression))

        # tag tail (deferred)
        tail = self.tail
        if self.fill_slot is None:
            for part in reversed(tail):
                if isinstance(part, types.expression):
                    _.append(clauses.Write(part, defer=True))
                else:
                    _.append(clauses.Out(part, defer=True))
            
        # macro method
        macro = self.macro
        if macro is not None:
            _.append(clauses.Method(
                macro.name, macro.args))
                
        # condition
        if self.condition is not None:
            _.append(clauses.Condition(self.condition))

        # repeat
        if self.repeat is not None:
            variables, expression = self.repeat
            if len(variables) != 1:
                raise ValueError(
                    "Cannot unpack more than one variable in a "
                    "repeat statement.")
            _.append(clauses.Repeat(variables[0], expression))

        content = self.content

        # macro slot definition
        if self.define_slot:
            # check if slot has been filled
            variable = self.symbols.slot + self.define_slot
            if variable in itertools.chain(*self.stream.scope):
                content = types.value(variable)

        # set dynamic content flag
        dynamic = content or self.translate is not None

        # static attributes are at the bottom of the food chain
        attributes = utils.odict()
        attributes.update(self.static_attributes)

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
                if variable in dynamic_attr_names or variable in attributes:
                    text = '"%s"' % attributes[variable]
                    expression = self.translate_expression(text)
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
                self.element.tag, attributes,
                expression=self.dict_attributes, selfclosing=selfclosing,
                cdata=self.cdata is not None)
            if self.omit:
                _.append(clauses.Condition(
                    types.value("not (%s)" % self.omit), [tag], finalize=False))
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

        # include
        elif self.include:
            # compute macro function arguments and create argument string
            arguments = ", ".join(
                ("%s=%s" % (arg, arg) for arg in \
                 itertools.chain(*self.stream.scope)))

            # XInclude's are similar to METAL macros, except the macro
            # is always defined as the entire template.

            # first we compute the filename expression and write it to
            # an internal variable
            _.append(clauses.Assign(self.include, self.symbols.include))

            # call template
            _.append(clauses.Write(
                types.template(
                "%%(xincludes)s.get(%%(include)s, %s).render_xinclude(%s)" % \
                (repr(self.format), arguments))))
            
        # use macro
        elif self.use_macro:
            # for each fill-slot element, create a new output stream
            # and save value in a temporary variable
            kwargs = []
            for element in self.element.xpath(
                './/*[@metal:fill-slot] | .//metal:*[@fill-slot]',
                namespaces={'metal': config.METAL_NS}):
                if element.node.fill_slot is None:
                    # XXX this should not be necessary, but the above
                    # xpath expression finds non-"metal:fill-slot"
                    # nodes somehow on my system; this is perhaps due
                    # to a bug in the libxml2 version I'm using; we
                    # work around it by just skipping the element.
                    # (chrism)
                    continue

                variable = self.symbols.slot+element.node.fill_slot
                kwargs.append((variable, variable))
                
                subclauses = []
                subclauses.append(clauses.Define(
                    types.declaration((self.symbols.out, self.symbols.write)),
                    types.template('%(init)s.initialize_stream()')))
                subclauses.append(clauses.Visit(element.node))
                subclauses.append(clauses.Assign(
                    types.template('%(out)s.getvalue()'), variable))
                _.append(clauses.Group(subclauses))
                
            _.append(clauses.Assign(self.use_macro, self.symbols.metal))

            # compute macro function arguments and create argument string
            if 'xmlns' in self.element.attrib:
                kwargs.append(('include_ns_attribute', repr(True)))
                
            arguments = ", ".join(
                tuple("%s=%s" % (arg, arg) for arg in \
                      itertools.chain(*self.stream.scope))+
                tuple("%s=%s" % kwarg for kwarg in kwargs))

            _.append(clauses.Write(
                types.value("%s.render(%s)" % (self.symbols.metal, arguments))))

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

                subclauses = []
                subclauses.append(clauses.Define(
                    types.declaration((self.symbols.out, self.symbols.write)),
                    types.template('%(init)s.initialize_stream()')))
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
            _.append(clauses.Condition(condition,
                        [clauses.UnicodeWrite(result)]))

            subclauses = []
            if self.element.text:
                subclauses.append(clauses.Out(self.element.text))
            for element in self.element:
                name = element.node.translation_name
                if name:
                    value = types.value("%s['%s']" % (mapping, name))
                    subclauses.append(clauses.Write(value))
                else:
                    subclauses.append(clauses.Out(element.tostring()))
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

        out = StringIO(self.element.text)
        
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
    implicit_doctype = ""
    
    def __init__(self, body, parser, implicit_doctype=None,
                 explicit_doctype=None, encoding=None):
        # documents without a document type declaration are augmented
        # with default namespace declarations and proper XML entity
        # definitions; this represents a 'convention' over
        # 'configuration' approach to template documents
        no_doctype_declaration = '<!DOCTYPE' not in body

        # add default namespace declaration if no explicit document
        # type has been set
        if implicit_doctype and explicit_doctype is None and \
               no_doctype_declaration:
            body = """\
            <meta:declare-ns
            xmlns="%s" xmlns:tal="%s" xmlns:metal="%s" xmlns:i18n="%s"
            xmlns:py="%s" xmlns:xinclude="%s" xmlns:meta="%s"
            >%s</meta:declare-ns>""" % (
                config.XHTML_NS, config.TAL_NS,
                config.METAL_NS, config.I18N_NS,
                config.PY_NS, config.XI_NS, config.META_NS,
                body)

        # prepend the implicit doctype to the document source and add
        # entity definitions
        if implicit_doctype and no_doctype_declaration:
            entities = "".join((
                '<!ENTITY %s "&#%s;">' % (name, text) for (name, text) in \
                htmlentitydefs.name2codepoint.items()))

            implicit_doctype = implicit_doctype[:-1] + '  [ %s ]>' % entities
            self.implicit_doctype = implicit_doctype
            body = implicit_doctype + "\n" + body

        # parse document
        self.root, parsed_doctype = parser.parse(body)

        # explicit document type has priority
        if explicit_doctype is not None:
            self.doctype = explicit_doctype
        elif parsed_doctype and not no_doctype_declaration:
            self.doctype = parsed_doctype
            
        self.parser = parser

        if utils.coerces_gracefully(encoding):
            self.encoding = None
        else:
            self.encoding = encoding
        
    @classmethod
    def from_text(cls, body, parser, **kwargs):
        compiler = Compiler(
            "<html xmlns='%s'></html>" % config.XHTML_NS, parser,
            implicit_doctype=None, encoding=kwargs.get('encoding'))
        compiler.root.text = body
        compiler.root.meta_omit = ""
        return compiler

    def __call__(self, macro=None, global_scope=True, parameters=()):
        if not isinstance(self.root, Element):
            raise ValueError(
                "Must define valid namespace for tag: '%s.'" % self.root.tag)

        # if macro is non-trivial, start compilation at the element
        # where the macro is defined
        if macro:
            elements = self.root.xpath(
                'descendant-or-self::*[@metal:define-macro="%s"] |'
                'descendant-or-self::metal:*[@define-macro="%s"]' % (macro, macro),
                namespaces={'metal': config.METAL_NS})

            if not elements:
                raise ValueError("Macro not found: %s." % macro)

            self.root = element = elements[0]

            # remove attribute from tag
            if element.nsmap[element.prefix] == config.METAL_NS:
                del element.attrib['define-macro']
            else:
                del element.attrib[utils.metal_attr('define-macro')]
                
        if macro is None or 'include_ns_attribute' in parameters:
            # add namespace attribute to 
            namespace = self.root.tag.split('}')[0][1:]
            self.root.attrib['xmlns'] = namespace
        
        if global_scope:
            wrapper = generation.template_wrapper
        else:
            wrapper = generation.macro_wrapper
            
        # initialize code stream object
        stream = generation.CodeIO(
            self.root.node.symbols, encoding=self.encoding,
            indentation=1, indentation_string="\t")

        # initialize variable scope
        stream.scope.append(set(
            (stream.symbols.out, stream.symbols.write, stream.symbols.scope) + \
            tuple(parameters)))

        # output doctype if any
        if self.doctype and not macro:
            doctype = self.doctype + '\n'
            if self.encoding:
                doctype = doctype.encode(self.encoding)
            out = clauses.Out(doctype)
            stream.scope.append(set())
            stream.begin([out])
            stream.end([out])
            stream.scope.pop()

        # start generation
        self.root.start(stream)
        body = stream.getvalue()

        # remove namespace declaration
        if 'xmlns' in self.root.attrib:
            del self.root.attrib['xmlns']
        
        # prepare args
        ignore = 'target_language',
        args = ', '.join((param for param in parameters if param not in ignore))
        if args:
            args += ', '

        # prepare kwargs
        kwargs = ', '.join("%s=None" % param for param in parameters)
        if kwargs:
            kwargs += ', '

        # prepare selectors
        extra = ''
        for selector in stream.selectors:
            extra += '%s=None, ' % selector

        # wrap generated Python-code in function definition
        mapping = dict(
            args=args, kwargs=kwargs, extra=extra, body=body)
        mapping.update(stream.symbols.__dict__)
        source = wrapper % mapping

        # serialize document
        xmldoc = self.implicit_doctype + "\n" + self.root.tostring()

        return ByteCodeTemplate(
            source, stream.symbol_mapping,
            xmldoc, self.parser, self.root)

class ByteCodeTemplate(object):
    """Template compiled to byte-code."""

    def __init__(self, source, symbols, xmldoc, parser, tree):
        # compile code
        suite = codegen.Suite(source, globals=symbols)
        suite._globals.update(symbols)
        
        # execute code
        _locals = {}
        exec suite.code in suite._globals, _locals

        # keep state
        self.func = _locals['render']
        self.source = source
        self.symbols = symbols
        self.xmldoc = xmldoc
        self.parser = parser
        self.tree = tree
            
    def __reduce__(self):
        reconstructor, (cls, base, state), kwargs = \
                       GhostedByteCodeTemplate(self).__reduce__()
        return reconstructor, (ByteCodeTemplate, base, state), kwargs

    def __setstate__(self, state):
        self.__dict__.update(GhostedByteCodeTemplate.rebuild(state))

    def __repr__(self):
        return '<%s parser="%s">' % \
               (type(self).__name__, str(type(self.parser)).split("'")[1])

    def render(self, *args, **kwargs):
        kwargs.update(self.selectors)
        return self.func(generation, *args, **kwargs)

    @property
    def selectors(self):
        selectors = getattr(self, '_selectors', None)
        if selectors is not None:
            return selectors

        self._selectors = selectors = {}
        for element in self.tree.xpath(
            './/*[@meta:select]', namespaces={'meta': config.META_NS}):
            name = element.attrib[utils.meta_attr('select')]
            selectors[name] = element.xpath

        return selectors

class GhostedByteCodeTemplate(object):
    suite = codegen.Suite("def render(): pass")
    
    def __init__(self, template):
        self.code = marshal.dumps(template.func.func_code)
        self.defaults = len(template.func.func_defaults or ())
        self.symbols = template.symbols
        self.source = template.source
        self.xmldoc = template.xmldoc
        self.parser = template.parser
        
    @classmethod
    def rebuild(cls, state):
        symbols = state['symbols']
        source = state['source']
        xmldoc = state['xmldoc']
        parser = state['parser']
        tree, doctype = parser.parse(xmldoc)        

        _locals = {}
        _globals = symbols.copy()
        _globals.update(cls.suite._globals)
        exec cls.suite.code in _globals, _locals
        
        func = _locals['render']
        func.func_defaults = ((None,)*state['defaults']) or None
        func.func_code = marshal.loads(state['code'])

        return dict(
            func=func,
            symbols=symbols,
            source=source,
            xmldoc=xmldoc,
            parser=parser,
            tree=tree)

            
