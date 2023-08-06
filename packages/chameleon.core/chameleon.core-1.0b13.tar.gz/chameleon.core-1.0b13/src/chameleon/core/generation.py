from zope.i18n import interpolate
from zope.i18n import translate
from zope.i18nmessageid import Message

import utils
import types

function_template = """\
def bind():
%(imports)s
\tdef %(name)s(%(arguments)s):
%(source)s
%(return)s
\treturn %(name)s
"""

def indent_block(text, level=2):
    return "\n".join(("\t" * level + s for s in text.split('\n')))
                     
def function_wrap(name, args, imports, source, return_expr=""):
    format_values = {
        'name': name,
        'imports': indent_block('\n'.join(imports), 1),
        'arguments': ', '.join(args),
        'source': indent_block(source),
        'return': indent_block("return %s" % return_expr)}
    
    return function_template % format_values

class Marker(object):
    def __nonzero__(self):
        return False

marker = Marker()

def fast_translate(msgid, domain=None, mapping=None, context=None,
                   target_language=None, default=None):
    """This translation function does not attempt to negotiate a
    language if ``None`` is passed."""
    
    if target_language is not None:
        return translate(
            msgid, domain=domain, mapping=mapping, context=context,
            target_language=target_language, default=default)
    
    if isinstance(msgid, Message):
        default = msgid.default
        mapping = msgid.mapping

    if default is None:
        default = unicode(msgid)

    if not isinstance(default, basestring):
        return default
    
    return interpolate(default, mapping)

def initialize_tal():
    return ({}, utils.repeatdict())

def initialize_stream():
    out = BufferIO()
    return (out, out.write)

initialize_scope = utils.econtext
    
class BufferIO(list):
    write = list.append

    def getvalue(self):
        return ''.join(self)
        
class CodeIO(BufferIO):
    """Stream buffer suitable for writing Python-code. This class is
    used internally by the compiler to manage variable scopes, source
    annotations and temporary variables."""

    t_prefix = '_tmp'
    v_prefix = '_tmpv'

    annotation = None
    
    def __init__(self, symbols=None, encoding=None,
                 indentation=0, indentation_string="\t"):
        BufferIO.__init__(self)
        self.symbols = symbols or object
        self.symbol_mapping = {}
        self.encoding = encoding
        self.indentation = indentation
        self.indentation_string = indentation_string
        self.queue = []
        self.scope = [set()]
        self.annotations = {}
        self._variables = {}
        self.t_counter = 0
        self.v_counter = 0
        self.l_counter = 0

    def new_var(self):
        self.v_counter += 1
        return "%s%d" % (self.v_prefix, self.v_counter)
        
    def save(self):
        self.t_counter += 1
        return "%s%d" % (self.t_prefix, self.t_counter)

    def restore(self):
        var = "%s%d" % (self.t_prefix, self.t_counter)
        self.t_counter -= 1
        return var

    def indent(self, amount=1):
        if amount > 0:
            self.flush()
            self.indentation += amount

    def outdent(self, amount=1):
        if amount > 0:
            self.flush()
            self.indentation -= amount

    def annotate(self, annotation):
        if annotation.label is not None:
            annotation = annotation.label

        # make sure the annotation is a base string type
        if isinstance(annotation, unicode):
            annotation = unicode(annotation)
        else:
            annotation = str(annotation)

        # encode unicode string if required
        if isinstance(annotation, unicode) and self.encoding:
            annotation = annotation.encode(self.encoding)
            
        self.annotation = self.annotations[self.l_counter] = annotation

    def out(self, value):
        if isinstance(value, types.expression):
            assert isinstance(value, types.value)
        elif isinstance(value, unicode) and self.encoding:
            value = value.encode(self.encoding)
        self.queue.append(value)
            
    def flush(self):
        if self.queue:
            # optimize queue to merge adjacent strings
            optimized = []
            
            current = None
            while self.queue:
                next = self.queue.pop(0)

                if isinstance(current, basestring) and isinstance(next, basestring):
                    current = current + next
                    continue
                elif current is not None:
                    optimized.append(current)

                current = next
            else:
                optimized.append(current)            

            assert len(self.queue) == 0
            
            self.write(
                "%s(%s)" %
                (self.symbols.write, " + ".join(
                isinstance(expression, types.value) and expression or \
                repr(expression) for expression in optimized)))

    def write(self, string):
        if isinstance(string, unicode) and self.encoding:
            string = string.encode(self.encoding)

        self.l_counter += len(string.split('\n'))-1
        self.flush()
        
        indent = self.indentation_string * self.indentation

        # if a source code annotation is set, write it as a
        # triple-quoted string prior to the source line
        if self.annotation:
            if isinstance(self.annotation, unicode) and self.encoding:
                self.annotation = self.annotation.encode(self.encoding)
            BufferIO.write(
                self, "%s%s\n" % (indent, repr(self.annotation)))
            self.annotation = None
            
        BufferIO.write(self, indent + string + '\n')

    def getvalue(self):
        self.flush()
        return BufferIO.getvalue(self)

    def escape(self, variable):
        self.write("if '&' in %s:" % variable)
        self.indent()
        self.write("%s = %s.replace('&', '&amp;')" % (variable, variable))
        self.outdent()
        self.write("if '<' in %s:" % variable)
        self.indent()
        self.write("%s = %s.replace('<', '&lt;')" % (variable, variable))
        self.outdent()
        self.write("if '>' in %s:" % variable)
        self.indent()
        self.write("%s = %s.replace('>', '&gt;')" % (variable, variable))
        self.outdent()
        self.write("if '\"' in %s:" % variable)
        self.indent()
        self.write("%s = %s.replace('\"', '&quot;')" % (variable, variable))
        self.outdent()

    def convert_to_string(self, variable):
        self.write("if isinstance(%s, unicode):" % variable)
        self.indent()
        self.write("%s = %s.encode('%s')" % (variable, variable, self.encoding))
        self.outdent()

    def coerce_to_string(self, variable):
        self.write("if isinstance(%s, unicode):" % variable)
        self.indent()
        self.write("%s = %s.encode('%s')" % (variable, variable, self.encoding))
        self.outdent()
        self.write("elif not isinstance(%s, str):" % variable)
        self.indent()
        self.write("%s = str(%s)" % (variable, variable))
        self.outdent()

    def coerce_to_unicode(self, variable):
        """Coerces variable to unicode (actually ``str``, because it's
        much faster)."""
        
        self.write("if not isinstance(%s, basestring):" % variable)
        self.indent()
        self.write("%s = str(%s)" % (variable, variable))
        self.outdent()
        
    def begin(self, clauses):
        if isinstance(clauses, (list, tuple)):
            for clause in clauses:
                self.begin(clause)
        else:
            clauses.begin(self)
                
    def end(self, clauses):
        if isinstance(clauses, (list, tuple)):
            for clause in reversed(clauses):
                self.end(clause)
        else:
            clauses.end(self)
