import htmlentitydefs
import config
import utils
import base64

import lxml.etree
import xml.parsers.expat

from cPickle import dumps, loads
from StringIO import StringIO

# this exception is imported for historic reasons
XMLSyntaxError = lxml.etree.XMLSyntaxError

def import_elementtree():
    """The ElementTree is used to validate output in debug-mode. We
    attempt to load the library from several locations."""
    
    try:
        import xml.etree.ElementTree as ET
    except:
        try:
            import elementtree.ElementTree as ET
        except ImportError:
            import cElementTree as ET
        
    return ET

def validate(string):
    """Wraps string as a proper HTML document and validates it by
    attempting to parse it using the active ElementTree parser."""
    
    validation_string = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd" [ %s ]><div>%s</div>' % (
        utils.entities, string)
    
    try:
        import_elementtree().fromstring(validation_string)
    except xml.parsers.expat.ExpatError:
        raise ValidationError(string)

class ExpatParser(object):
    """XML tree parser using the ``xml.parsers.expat`` stream
    parser. This parser serve to accept template input which lacks a
    proper prefix namespace mapping or entity definitions. It also
    works around an issue where the expat parser incorrectly parses an
    element with trivial body text as self-closing."""
    
    root = None
    index = None
    
    # doctype
    doctype = None

    # xml-declaration
    xml_version = None
    encoding = None
    standalone = None

    def __init__(self, parser, body, expat):
        self.parser = parser
        self.body = body
        self.expat = expat
        
    def _get_element(self):
        try:
            return self._element
        except AttributeError:
            raise xml.parsers.expat.ExpatError(
                "Unable to parse document; no start-tag found.")

    def _set_element(self, element):
        self._element = element

    element = property(_get_element, _set_element)

    def StartElementHandler(self, tag, attrs):
        # update prefix to namespace mapping
        if self.root is None:
            self.index = self.expat.CurrentByteIndex
            nsmap = {}
        else:
            nsmap = self.root.nsmap.copy()

        # process namespace declarations
        for key, value in attrs.items():
            if key.startswith('xmlns:'):
                prefix, name = key.split(':')
                nsmap[name] = value
                del attrs[key]
            
        for key, value in attrs.items():
            try:
                prefix, name = key.split(':')
            except (ValueError, TypeError):
                continue

            del attrs[key]

            try:
                namespace = nsmap.get(prefix) or config.DEFAULT_NS_MAP[prefix]
            except KeyError:
                raise KeyError(
                    "Attribute prefix unknown: '%s'." % prefix)
            attrs['{%s}%s' % (namespace, name)] = value
        
        # process tag
        try:
            prefix, name = tag.split(':')
            namespace = nsmap.get(prefix) or config.DEFAULT_NS_MAP[prefix]
            tag = '{%s}%s' % (namespace, name)
        except ValueError:
            pass
                
        # create element using parser
        element = self.parser.makeelement(tag, attrs, nsmap=nsmap)

        if self.root is None:
            document = []

            declaration = filter(
                lambda (key, value): value is not None, 
                (('version', self.xml_version),
                 ('encoding', self.encoding),
                 ('standalone', self.standalone)))

            if declaration:
                document.append(
                    '<?xml %s?>' % "".join(
                        '%s="%s" ' % pair for pair in declaration))

            if self.doctype:
                document.append(self.doctype)

            # render element
            document.append(element.tostring())
                
            # parse document
            self.parser.feed("\n".join(document))
            element = self.parser.close()

            # set this element as tree root
            self.root = element
        else:
            self.element.append(element)

        # set as current element
        self.element = element

    def EndElementHandler(self, name):
        if self.element.text is None and self.body[
            self.expat.CurrentByteIndex-2] != '/':
            self.element.text = ""
        self.element = self.element.getparent()

    def CharacterDataHandler(self, data):
        if len(self.element) == 0:
            current = self.element.text or ""
            self.element.text = current + data
        else:
            current = self.element[-1].tail or ""
            self.element[-1].tail = current + data
            
    def ProcessingInstructionHandler(self, target, data):
        self.element.append(
            lxml.etree.PI(target, data))        
        
    def StartCdataSectionHandler(self):
        element = self.parser.makeelement(
            utils.xhtml_attr('cdata'))
        element.meta_cdata = ""
        self.element.append(element)
        self.element = element            

    def EndCdataSectionHandler(self):
        self.element = self.element.getparent()

    def CommentHandler(self, text):
        if self.root is not None and self.element is not None:
            self.element.append(
                lxml.etree.Comment(text))
        
    def XmlDeclHandler(self, xml_version, encoding, standalone):
        self.xml_version = xml_version
        self.encoding = encoding

        if standalone:
            self.standalone = 'yes'
        else:
            self.standalone = 'no'
        
    def ExternalEntityRefHandler(self, context, base, sysid, pubid):
        parser = self.expat.ExternalEntityParserCreate(context)
        parser.ProcessingInstructionHandler = self.ProcessingInstructionHandler
        parser.ParseFile(StringIO(utils.entities))
        return 1

    def DefaultHandler(self, userdata):
        if userdata.startswith('&'):
            return self.CharacterDataHandler(userdata)            
                
    def StartDoctypeDeclHandler(self, *args):
        doctype_name, sysid, pubid, has_internal_subset = args
        self.doctype = '<!DOCTYPE %s PUBLIC "%s" "%s">' % (
            doctype_name, pubid, sysid)
        
class ValidationError(ValueError):
    def __str__(self):
        value, = self.args
        return "Insertion of %s is not allowed." % \
               repr(value)

class Parser(object):
    element_mapping = utils.emptydict()
    fallback = None
    
    def serialize(self, tree):
        return serialize(tree)

    def parse_xml(self, body):
        return self.parse(body)
    
    def parse_text(self, text):
        tree = self.parse('<html xmlns="%s"></html>' % config.XHTML_NS)
        tree.getroot().text = text
        tree.getroot().meta_omit = ""
        return tree
        
    def parse(self, body):
        return parse(body, self.element_mapping, fallback=self.fallback)

    # for backwards-compatibility, the parser object must be callable
    # which invokes the ``parse``-method
    def __call__(self, body):
        return self.parse(body)
    
class Annotation(property):
    def __init__(self, name, default=None):
        property.__init__(self, self._get, self._set)
        self.name = name
        self.default = default

    def _get(instance, element):
        value = element.attrib.get(instance.name)
        if value is not None:
            return loads(base64.decodestring(value))
        return instance.default

    def _set(instance, element, value):
        element.attrib[instance.name] = base64.encodestring(dumps(value))

def elements_with_attribute(element, ns, name, value=None):
    if value is None:
        expression = 'descendant-or-self::*[@prefix:%s] '\
                     '| descendant-or-self::prefix:*[@%s]' % (
            name, name)
    else:
        expression = 'descendant-or-self::*[@prefix:%s="%s"] '\
                     '| descendant-or-self::prefix:*[@%s="%s"]' % (
            name, value, name, value)

    return element.xpath(
        expression,
        namespaces={'prefix': ns})

class ElementBase(lxml.etree.ElementBase):
    def tostring(self):
        return lxml.etree.tostring(self)

def parse(body, element_mapping, fallback=None):
    """Parse XML document using expat and build lxml tree."""
    
    # set up namespace lookup class
    lookup = lxml.etree.ElementNamespaceClassLookup(
        fallback=lxml.etree.ElementDefaultClassLookup(fallback))
    for key, mapping in element_mapping.items():
        lookup.get_namespace(key).update(mapping)

    # set up lxml parser
    parser = lxml.etree.XMLParser(resolve_entities=False, strip_cdata=False)
    parser.setElementClassLookup(lookup)

    junk = ""
    tree = None
    parts = []
    while tree is None:
        # set up expat parser
        expat = xml.parsers.expat.ParserCreate()
        expat.UseForeignDTD()
        expat.SetParamEntityParsing(
            xml.parsers.expat.XML_PARAM_ENTITY_PARSING_ALWAYS)

        # attach expat parser methods
        expatparser = ExpatParser(parser, body, expat)
        for name, value in type(expatparser).__dict__.items():
            if isinstance(value, property):
                continue
            try:
                setattr(expat, name, getattr(expatparser, name))
            except AttributeError:
                pass

        try:
            # attempt to parse this body; if we're not successful,
            # this may be because the document source consists of
            # several 'parts'; although this is not valid XML, we do
            # support it, being a template engine, not a XML
            # validator :-)
            expat.Parse(body, 1)

            if parts:
                parts.append(expatparser.root)
                root = parser.makeelement(
                    utils.meta_attr('fragments'))
                for i, part in enumerate(parts):
                    if isinstance(part, basestring):
                        parts[i-1].tail = part
                    else:
                        root.append(part)
                tree = root.getroottree()
            else:
                tree = expatparser.root.getroottree()
        except xml.parsers.expat.ExpatError:
            # if we are not able to find a tree root, we give up and
            # let the exception through
            if expatparser.root is None:
                raise

            # add the root as a tree fragment and update the body
            # source to the next possible chunk
            parts.append(expatparser.root)
            body = body[:expatparser.index] + body[expat.CurrentByteIndex:]

            # a simple heuristic is used here to allow chunks of
            # 'junk' in-between the tree fragments
            pos = body.find('<')
            junk = body[:pos]
            body = body[pos:]
            parts.append(junk)
            
    return tree

def serialize(tree):
    """Serialize tree using lxml."""
    
    return lxml.etree.tostring(tree, encoding='utf-8')
