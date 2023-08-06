# -*- coding: utf-8 -*-

import zope.interface
import zope.component
import zope.security
import zope.security.proxy
import zope.traversing.adapters

import parser
import re

import interfaces
import types

_marker = object()

class ExpressionTranslation(object):
    zope.interface.implements(interfaces.IExpressionTranslation)

    re_pragma = re.compile(r'^\s*(?P<pragma>[a-z]+):\s*')
    re_interpolation = re.compile(r'(?P<prefix>[^\\]\$|^\$){((?P<expression>.*)})?')

    def name(self, string):
        return string
    
    def search(self, string):
        """
        We need to implement a ``validate``-method. Let's define that an
        expression is valid if it contains an odd number of
        characters.
        
          >>> class MockExpressionTranslation(ExpressionTranslation):
          ...     def validate(self, string):
          ...         if len(string) % 2 == 0: raise SyntaxError()

          >>> search = MockExpressionTranslation().search
          >>> search("a")
          'a'
          >>> search("ab")
          'a'
          >>> search("abc")
          'abc'
          
        """

        left = 0
        right = left + 1

        current = None

        while right <= len(string):
            expression = string[left:right]

            try:
                e = self.validate(expression)
                current = expression
            except SyntaxError, e:
                if right == len(string):
                    if current is not None:
                        return current

                    raise e

            right += 1

        return current

    def declaration(self, string):
        """
          >>> declaration = ExpressionTranslation().declaration

        Single variable:

          >>> declaration("variable")
          declaration('variable',)

        Multiple variables:

          >>> declaration("variable1, variable2")
          declaration('variable1', 'variable2')

        Repeat not allowed:

          >>> declaration('repeat')
          Traceback (most recent call last):
          ...
          ValueError: Invalid variable name 'repeat' (reserved).

          >>> declaration('_disallowed')
          Traceback (most recent call last):
          ...
          ValueError: Invalid variable name '_disallowed' (starts with an underscore).
        """

        variables = []
        for var in string.split(', '):
            var = var.strip()

            if var in ('repeat',):
                raise ValueError, "Invalid variable name '%s' (reserved)." % var

            if var.startswith('_') and not var.startswith('_tmp'):
                raise ValueError(
                    "Invalid variable name '%s' (starts with an underscore)." % var)

            variables.append(var)

        return types.declaration(variables)

    def mapping(self, string):
        """
          >>> mapping = ExpressionTranslation().mapping
          
          >>> mapping("abc def")
          mapping(('abc', 'def'),)

          >>> mapping("abc def;")
          mapping(('abc', 'def'),)

          >>> mapping("abc")
          mapping(('abc', None),)

          >>> mapping("abc;")
          mapping(('abc', None),)

          >>> mapping("abc; def ghi")
          mapping(('abc', None), ('def', 'ghi'))

        """

        defs = string.split(';')
        mappings = []
        for d in defs:
            d = d.strip()
            if d == '':
                continue

            while '  ' in d:
                d = d.replace('  ', ' ')

            parts = d.split(' ')
            if len(parts) == 1:
                mappings.append((d, None))
            elif len(parts) == 2:
                mappings.append((parts[0], parts[1]))
            else:
                raise ValueError, "Invalid mapping (%s)." % string

        return types.mapping(mappings)

    def definitions(self, string):
        """
        
        >>> class MockExpressionTranslation(ExpressionTranslation):
        ...     def expression(self, string):
        ...         return types.value(string.strip())
        
        >>> definitions = MockExpressionTranslation().definitions
        
        Single define:
        
        >>> definitions("variable expression")
        definitions((declaration('variable',), value('expression')),)
        
        Multiple defines:
        
        >>> definitions("variable1 expression1; variable2 expression2")
        definitions((declaration('variable1',), value('expression1')),
                    (declaration('variable2',), value('expression2')))
        
        Tuple define:
        
        >>> definitions("(variable1, variable2) (expression1, expression2)")
        definitions((declaration('variable1', 'variable2'),
                    value('(expression1, expression2)')),)
        
        A define clause that ends in a semicolon:
        
        >>> definitions("variable expression;")
        definitions((declaration('variable',), value('expression')),)
        
        A define clause with a trivial expression (we do allow this):
        
        >>> definitions("variable")
        definitions((declaration('variable',), None),)
        
        A proper define clause following one with a trivial expression:
        
        >>> definitions("variable1 expression; variable2")
        definitions((declaration('variable1',), value('expression')),
                    (declaration('variable2',), None))

        """

        string = string.replace('\n', '').strip()

        defines = []

        i = 0
        while i < len(string):
            while string[i] == ' ':
                i += 1

            # get variable definition
            if string[i] == '(':
                j = string.find(')', i+1)
                if j == -1:
                    raise ValueError, "Invalid variable tuple definition (%s)." % string
                var = self.declaration(string[i+1:j])
                j += 1
            else:
                j = string.find(' ', i + 1)
                if j == -1:
                    var = self.declaration(string[i:])
                    j = len(string)
                else:
                    var = self.declaration(string[i:j])

            # get expression
            i = j
            while j < len(string):
                j = string.find(';', j+1)
                if j == -1:
                    j = len(string)

                try:
                    expr = self.expression(string[i:j])
                except SyntaxError, e:
                    if j < len(string):
                        continue
                        
                    raise e
                break
            else:
                expr = None

            defines.append((var, expr))

            i = j + 1

        return types.definitions(defines)

    def definition(self, string):
        defs = self.definitions(string)
        if len(defs) != 1:
            raise ValueError, "Multiple definitions not allowed."

        return defs[0]

    def output(self, string):
        """
        >>> class MockExpressionTranslation(ExpressionTranslation):
        ...     def validate(self, string):
        ...         return True
        ...
        ...     def translate(self, string):
        ...         return types.value(string)

        >>> output = MockExpressionTranslation().output

        >>> output("context/title")
        escape(value('context/title'),)

        >>> output("context/pretty_title_or_id|context/title")
        escape(value('context/pretty_title_or_id'), value('context/title'))

        >>> output("structure context/title")
        value('context/title')
        
        """
        
        if string.startswith('structure '):
            return self.expression(string[len('structure'):])
        
        expression = self.expression(string)

        if isinstance(expression, types.parts):
            return types.escape(expression)

        return types.escape((expression,))
            
    def expression(self, string):
        """We need to implement the ``validate`` and
        ``translate``-methods. Let's define that an expression is
        valid if it contains an odd number of characters.
        
        >>> class MockExpressionTranslation(ExpressionTranslation):
        ...     def validate(self, string):
        ...         return True
        ...
        ...     def translate(self, string):
        ...         return types.value(string)

        >>> expression = MockExpressionTranslation().expression

        >>> expression('a')
        value('a')

        >>> expression('a|b')
        parts(value('a'), value('b'))
    
        """

        string = string.replace('\n', '').strip()

        if not string:
            return types.parts()

        parts = []

        # default translator is ``self``
        translator = self

        i = j = 0
        while i < len(string):
            if translator is self:
                match = self.re_pragma.match(string[i:])
                if match is not None:
                    pragma = match.group('pragma')

                    translator = \
                        zope.component.queryUtility(
                            interfaces.IExpressionTranslation, name=pragma) or \
                        zope.component.queryAdapter(
                            self, interfaces.IExpressionTranslation, name=pragma)
                    
                    if translator is not None:
                        i += match.end()
                        continue

                    translator = self

            j = string.find('|', j + 1)
            if j == -1:
                j = len(string)

            expr = string[i:j].lstrip()

            try:
                translator.validate(expr)
            except Exception, e:
                if j < len(string):
                    continue

                raise e

            value = translator.translate(expr)
            parts.append(value)
            translator = self
            
            i = j + 1

        if len(parts) == 1:
            return parts[0]

        return types.parts(parts)

    def interpolate(self, string):
        """Search for an interpolation and return a match.

        >>> class MockExpressionTranslation(ExpressionTranslation):
        ...     def validate(self, string):
        ...         if '}' in string: raise SyntaxError
        ...
        ...     def translate(self, string):
        ...         return types.value(string)

        >>> interpolate = MockExpressionTranslation().interpolate
        
        >>> interpolate('${abc}').group('expression')
        'abc'

        >>> interpolate('abc${def}').group('expression')
        'def'

        >>> interpolate('abc${def}ghi${jkl}').group('expression')
        'def'

        >>> interpolate('${abc')
        Traceback (most recent call last):
          ...
        SyntaxError: Interpolation expressions must of the form ${<expression>} (${abc)
        
        """

        m = self.re_interpolation.search(string)
        if m is None:
            return None

        expression = m.group('expression')

        if expression:
            left = m.start()+len(m.group('prefix'))
            exp = self.search(string[left+1:])
            right = left+2+len(exp)
            m = self.re_interpolation.search(string[:right])
            
        if expression is None or m is None:
            raise SyntaxError(
                "Interpolation expressions must of the "
                "form ${<expression>} (%s)" % string)

        return m

class PythonTranslation(ExpressionTranslation):
    def validate(self, string):
        """We use the ``parser`` module to determine if
        an expression is a valid python expression."""
        
        parser.expr(string.encode('utf-8'))

    def translate(self, string):
        if isinstance(string, unicode):
            string = string.encode('utf-8')

        return types.value(string)
            
class StringTranslation(ExpressionTranslation):
    zope.component.adapts(interfaces.IExpressionTranslation)

    def __init__(self, translator):
        self.translator = translator

    def validate(self, string):
        self.interpolate(string)

    def translate(self, string):
        return types.join(self.split(string))
        
    def split(self, string):
        """Split up an interpolation string expression into parts that
        are either unicode strings or ``value``-tuples.

        >>> class MockTranslation(ExpressionTranslation):
        ...     def validate(self, string):
        ...         if '}' in string: raise SyntaxError
        ...
        ...     def translate(self, string):
        ...         return types.value(string)
        
        >>> class MockStringTranslation(StringTranslation):
        ...     pass
        
        >>> split = MockStringTranslation(MockTranslation()).split

        >>> split("${abc}")
        (value('abc'),)

        >>> split("abc${def}")
        ('abc', value('def'))

        >>> split("${def}abc")
        (value('def'), 'abc')

        >>> split("abc${def}ghi")
        ('abc', value('def'), 'ghi')

        >>> split("abc${def}ghi${jkl}")
        ('abc', value('def'), 'ghi', value('jkl'))

        >>> split("abc${def | ghi}")
        ('abc', parts(value('def '), value('ghi')))

        >>> print split("abc${La Peña}")
        ('abc', value('La Pe\\xc3\\xb1a'))
        
        """

        m = self.translator.interpolate(string)
        if m is None:
            return (string,)

        parts = []
        
        start = m.start()
        if start > 0:
            text = string[:m.start()+1]
            parts.append(text)

        expression = m.group('expression')
        parts.append(self.translator.expression(expression))

        rest = string[m.end():]
        if len(rest):
            parts.extend(self.split(rest))

        return tuple(parts)

class PathTranslation(ExpressionTranslation):
    path_regex = re.compile(r'^((nocall|not):\s*)*([A-Za-z_]+)(/[A-Za-z_@-]+)*$')

    @classmethod
    def traverse(cls, base, request, call, *path_items):
        """See ``zope.app.pagetemplate.engine``."""

        _callable = callable(base)
        
        for i in range(len(path_items)):
            name = path_items[i]

            next = getattr(base, name, _marker)
            if next is not _marker:
                base = next()
            else:
                # special-case dicts for performance reasons        
                if getattr(base, '__class__', None) == dict:
                    base = base[name]
                else:
                    base = zope.traversing.adapters.traversePathElement(
                        base, name, path_items[i+1:], request=request)

            _callable = callable(base)

            if not isinstance(base, (basestring, tuple, list)):
                base = zope.security.proxy.ProxyFactory(base)

        if call and _callable:
            base = base()
                
        return base

    def validate(self, string):
        if not self.path_regex.match(string):
            raise SyntaxError("Not a valid path-expression.")

    def translate(self, string):
        """
            >>> translate = PathTranslation().translate
            >>> translate("a/b")
            value("_path(a, request, True, 'b')")

            >>> translate("context/@@view")
            value("_path(context, request, True, '@@view')")

            >>> translate("nocall: context/@@view")
            value("_path(context, request, False, '@@view')")

            >>> translate("not: context/@@view")
            value("not(_path(context, request, True, '@@view'))")

        """

        nocall = False
        negate = False

        while string:
            m = self.re_pragma.match(string)
            if m is None:
                break

            string = string[m.end():]
            pragma = m.group('pragma').lower()

            if pragma == 'nocall':
                nocall = True
            elif pragma == 'not':
                negate = True
            else:
                raise ValueError("Invalid pragma: %s" % pragma)

        parts = string.split('/')

        # map 'nothing' to 'None'
        parts = map(lambda part: part == 'nothing' and 'None' or part, parts)
        
        base = parts[0]
        components = [repr(part) for part in parts[1:]]

        if not components:
            components = ()

        value = types.value(
            '_path(%s, request, %s, %s)' % (base, not nocall, ', '.join(components)))

        if negate:
            value = types.value('not(%s)' % value)

        return value
