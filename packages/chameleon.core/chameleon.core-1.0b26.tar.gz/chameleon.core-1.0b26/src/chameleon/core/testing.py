import translation
import template
import generation
import etree
import config
import utils
import types

from StringIO import StringIO
from cPickle import dumps, loads

class TestCompiler(translation.Compiler):
    def __call__(self, *args, **kwargs):
        template = translation.Compiler.__call__(self, *args, **kwargs)
        template.compile()
        template = loads(dumps(template))
        return template

def pyexp(*exps):
    return types.parts([types.value(exp) for exp in exps])

def setup_stream(encoding=None):
    class symbols(translation.Node.symbols):
        out = '_out'
        write = '_write'

    out = StringIO()
    write = out.write
    stream = generation.CodeIO(symbols, encoding=encoding)
    stream.scope.append(set())
    return out, write, stream

def render_xhtml(body, **kwargs):
    template = compile_template(mock_parser.parse, body)
    return template.render(**kwargs)    
    
def render_text(body, **kwargs):
    template = compile_template(mock_parser.parse_text, body)
    return template.render(**kwargs)    

def compile_xhtml(body):
    return compile_template(mock_parser.parse, body)

def compile_template(parse_method, body, encoding=None,
                     macro=None, explicit_doctype=None, **kwargs):
    tree = parse_method(body)
    if '<?xml ' in body:
        xml_declaration = \
            """<?xml version="%s" encoding="%s" standalone="no" ?>""" % (
            tree.docinfo.xml_version, tree.docinfo.encoding)
    else:
        xml_declaration = None

    compiler = TestCompiler(
        tree, xml_declaration=xml_declaration,
        encoding=encoding, explicit_doctype=explicit_doctype)
    template = compiler(macro=macro, parameters=sorted(kwargs.keys()))    
    template.compile()
    
    return template

class MockElement(translation.Element):
    class Node(translation.Node):
        ns_omit = (
            "http://xml.zope.org/namespaces/meta",
            "http://www.w3.org/2001/XInclude")
        
        def __getattr__(self, name):
            return None

        @property
        def omit(self):
            if self.element.meta_omit is not None:
                return self.element.meta_omit or True
            if self.content:
                return True
            if self.include:
                return True

        @property
        def content(self):
            return self.element.meta_replace
        
        @property
        def cdata(self):
            return self.element.meta_cdata

        @property
        def include(self):
            href = self.element.xi_href
            if href is not None:
                return types.value(repr(href))

        @property
        def format(self):
            return self.element.xi_parse

    node = property(Node)

    xi_href = None
    xi_parse = None

class MockMetaElement(MockElement, translation.MetaElement):
    pass
    
class MockXiElement(MockElement):
    xi_href = utils.attribute('href')
    xi_parse = utils.attribute("parse", default="xml")

class MockParser(etree.Parser):
    element_mapping = {
        config.XHTML_NS: {None: MockElement},
        config.META_NS: {None: MockMetaElement},
        config.XI_NS: {None: MockXiElement}}

    fallback = MockElement
    
mock_parser = MockParser()

class MockMacros(template.Macros):
    def __getitem__(self, name):
        return self.get_macro(name)

class MockTemplate(object):
    def __init__(self, body, parser=mock_parser, doctype=None):
        self.body = body
        self.parser = parser
        self.doctype = doctype
        
    @property
    def macros(self):
        def render(name, parameters={}):
            template = compile_template(
                self.parser.parse, self.body, macro=name, **parameters)
            return template.render(**parameters)
        return MockMacros(render)

    def render(self, **kwargs):
        template = compile_template(
            self.parser.parse, self.body, explicit_doctype=self.doctype, **kwargs)
        return template.render(**kwargs)    

    __call__ = render
