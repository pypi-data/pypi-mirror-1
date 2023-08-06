from zope.i18n import interpolate
from zope.i18n import negotiate
from zope.i18n import translate
from zope.i18nmessageid import Message

import StringIO

import expressions
import utils

import z3c.pt.generation
from z3c.pt.config import DISABLE_I18N

wrapper = """\
def render(%starget_language=None):
\tglobal generation

\t(_out, _write) = generation.initialize_stream()
\t(_attributes, repeat) = generation.initialize_tal()
\t(_domain, _negotiate, _translate) = generation.initialize_i18n()
\t(_escape, _marker) = generation.initialize_helpers()
\t_path = generation.initialize_traversal()

\t_target_language = _negotiate(_context, target_language)
%s
\treturn _out.getvalue()
"""

def _fake_negotiate(context, target_language):
    return target_language

def _fake_translate(msgid, domain=None, mapping=None, context=None,
                    target_language=None, default=None):
    if isinstance(msgid, Message):
        default = msgid.default
        mapping = msgid.mapping

    if default is None:
        default = unicode(msgid)

    return interpolate(default, mapping)

def _negotiate(context, target_language):
    if target_language is not None:
        return target_language
    return negotiate(context)

def _escape(s, quote=0, string=1):
    """Replace special characters '&', '<' and '>' by SGML entities.

    If string is set to False, we are dealing with Unicode input.
    """
    if string:
        s = str(s)
    if '&' in s:
        s = s.replace("&", "&amp;") # Must be done first!
    if '<' in s:
        s = s.replace("<", "&lt;")
    if '>' in s:
        s = s.replace(">", "&gt;")
    if quote:
        s = s.replace('"', "&quot;")
    return s

def initialize_i18n():
    if DISABLE_I18N:
        return (None, _fake_negotiate, _fake_translate)
    return (None, _negotiate, translate)

def initialize_tal():
    return ({}, utils.repeatdict())

def initialize_helpers():
    return (_escape, object())

def initialize_stream():
    out = BufferIO()
    return (out, out.write)

def initialize_traversal():
    return expressions.PathTranslation.traverse

class Generator(object):
    def __init__(self, params):
        self.params = tuple(params)
        self.stream = CodeIO(indentation=1, indentation_string="\t")

        # initialize variable scope
        self.stream.scope.append(set(params + ['_out', '_write']))

    def __call__(self):
        # prepare template arguments
        args = self.params
        # We need to ensure we have _context for the i18n handling in the
        # arguments. The default template implementations pass this in
        # explicitly.
        if '_context' not in args:
            args = args + ('_context=None', )
        args = ', '.join(args)
        if args:
            args += ', '

        code = self.stream.getvalue()
        return wrapper % (args, code), {'generation': z3c.pt.generation}

class BufferIO(list):
    write = list.append

    def getvalue(self):
        return ''.join(self)

class CodeIO(StringIO.StringIO):
    """A I/O stream class that provides facilities to generate Python code.

    * Indentation is managed using ``indent`` and ``outdent``.

    * Annotations can be assigned on a per-line basis using ``annotate``.

    * Convenience methods for keeping track of temporary variables
   
    * Methods to process clauses (see ``begin`` and ``end``).
    
    """

    t_prefix = '_tmp'
    v_prefix = '_var'

    def __init__(self, indentation=0, indentation_string="\t"):
        StringIO.StringIO.__init__(self)
        self.indentation = indentation
        self.indentation_string = indentation_string
        self.queue = u''
        self.scope = [set()]
        self.annotations = {}
        
        self._variables = {}
        self.t_counter = 0
        self.l_counter = 0
        
    def save(self):
        self.t_counter += 1
        return "%s%d" % (self.t_prefix, self.t_counter)
        
    def restore(self):
        var = "%s%d" % (self.t_prefix, self.t_counter)
        self.t_counter -= 1
        return var
        
    def indent(self, amount=1):
        if amount > 0:
            self.cook()
            self.indentation += amount

    def outdent(self, amount=1):
        if amount > 0:
            self.cook()
            self.indentation -= amount

    def annotate(self, item):
        self.annotations[self.l_counter] = item

    def out(self, string):
        self.queue += string
        
    def cook(self):
        if self.queue:
            queue = self.queue
            self.queue = ''
            self.write("_write('%s')" %
                       queue.replace('\n', '\\n').replace("'", "\\'"))
            
    def write(self, string):
        if isinstance(string, str):
            string = string.decode('utf-8')

        self.l_counter += len(string.split('\n'))-1
        
        self.cook()
        StringIO.StringIO.write(
            self, self.indentation_string * self.indentation + string + '\n')

    def getvalue(self):
        self.cook()
        return StringIO.StringIO.getvalue(self)
            
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
        
