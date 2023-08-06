from zope import component

from StringIO import StringIO
import lxml.etree

import itertools
import generation
import clauses
import interfaces
import expressions
import types
import utils
import config

class Element(lxml.etree.ElementBase):
    """Base compiler element class.

    This class represents a node in the template tree. To start
    compilation at this node, use the ``start`` method, providing a
    code stream object.
    """

    _stream = None

    def start(self, stream):
        self._stream = stream
        self.visit()

    def update(self):
        self._preprocess_genshi()

    def begin(self):
        self.stream.scope.append(set())
        self.stream.begin(self._serialize())
        
    def end(self):
        self.stream.end(self._serialize())
        self.stream.scope.pop()

    def body(self):
        skip = self._replace or self._content or \
               self.i18n_translate is not None
        
        if not skip:
            for element in self:
                element.update()

            for element in self:
                element.visit()
                    
    def visit(self, skip_macro=True):
        assert self.stream is not None, "Must use ``start`` method."
        
        if skip_macro and self.py_def is not None:
            return

        for element in self:
            if isinstance(element, lxml.etree._Comment):
                self._wrap_comment(element)

        self.update()
        self.begin()
        self.body()
        self.end()

    @property
    def stream(self):
        root = self.getroottree().getroot()
        return root._stream
    
    @property
    def translator(self):
        while self.tal_default_expression is None:
            self = self.getparent()
            if self is None:
                raise ValueError("Default expression not set.")
            
        return component.getUtility(
            interfaces.IExpressionTranslation, name=self.tal_default_expression)

    def _preprocess_genshi(self):
        """Genshi preprocessing."""

        stream = self.stream
        
        # Step 1: Convert py:choose, py:when, py:otherwise into
        # tal:define, tal:condition
        choose_expression = self._pull_attribute(utils.py_attr('choose'))
        if choose_expression is not None:
            choose_variable = stream.save()
            
            if choose_expression:
                self._add_tal_define(choose_variable, choose_expression)
                
            # select all elements that have the "py:when" controller,
            # unless a "py:choose" expression sits in-between
            variables = []
            for element in self.xpath(
                './*[@py:when]|.//*[not(@py:choose)]/*[@py:when]',
                namespaces={'py': config.PY_NS}):

                expression = element._pull_attribute(utils.py_attr('when'))
                variable = stream.save()
                variables.append(variable)

                # add definition to ancestor
                self._add_tal_define(variable, expression)
                
                # add condition to element
                if choose_expression:
                    expression = "python: %s == %s" % (
                        choose_variable, variable)
                else:
                    expression = "python: %s" % variable
                    
                element.attrib[utils.tal_attr('condition')] = expression

            # process any "py:otherwise"-controllers
            for element in self.xpath(
                './*[@py:otherwise]|.//*[not(@py:choose)]/*[@py:otherwise]',
                namespaces={'py': config.PY_NS}):
                if choose_expression:
                    expression = "python: %s not in %s" % (
                        choose_variable, repr(tuple(variables)))
                else:
                    expression = "python: not(%s)" % " or ".join(variables)
                    
                element.attrib[utils.tal_attr('condition')] = expression

        # Step 2: Process "py:match" macros
        for element in self:
            if element.py_match is None:
                continue
            
            nsmap = element.nsmap.copy()

            # default namespace is not allowed in XPath
            nsmap['xmlns'] = nsmap[None]
            del nsmap[None]

            # define macro
            name = stream.save()
            element.attrib[utils.py_attr('def')] = "%s(select)" % name

            matches = self.getroottree().xpath(element.py_match, namespaces=nsmap)
            for match in matches:
                # save reference to bound xpath-function
                select = stream.save()
                stream.selectors[select] = match.xpath

                # replace matched element with macro
                expression = "%s(%s)" % (name, select)
                match.attrib[utils.tal_attr('replace')] = expression
                                
        # Step 3: Variable interpolation
        translator = self.translator
        
        if self.text is not None:
            while self.text:
                m = translator.interpolate(self.text)
                if m is None:
                    break

                t = parser.makeelement(utils.tal_attr('interpolation'))
                t.attrib['replace'] = m.group('expression')
                t.tail = self.text[m.end():]
                self.insert(0, t)
                t.update()

                if m.start() == 0:
                    self.text = self.text[1:m.start()+1]
                else:
                    self.text = self.text[:m.start()+1]

        if self.tail is not None:
            while self.tail:
                m = translator.interpolate(self.tail)
                if m is None:
                    break

                t = parser.makeelement(utils.tal_attr('interpolation'))
                t.attrib['replace'] = m.group('expression')
                t.tail = self.tail[m.end():]
                parent = self.getparent()
                parent.insert(parent.index(self)+1, t)
                t.update()
                                
                self.tail = self.tail[:m.start()+len(m.group('prefix'))-1]
                
        for name in self._get_static_attributes():
            value = self.attrib[name]

            if translator.interpolate(value):
                del self.attrib[name]

                attributes = utils.tal_attr('attributes')
                expr = '%s string: %s' % (name, value)
                if attributes in self.attrib:
                    self.attrib[attributes] += '; %s' % expr
                else:
                    self.attrib[attributes] = expr
                    
    def _serialize(self):
        """Serialize element into clause-statements."""
        
        _ = []

        # i18n domain
        if self.i18n_domain is not None:
            _.append(clauses.Define(
                "_domain", types.value(repr(self.i18n_domain))))

        # defines
        if self._define is not None:
            for variables, expression in self._define:
                _.append(clauses.Define(variables, expression))

        # macro
        for element in tuple(self):
            if not isinstance(element, Element):
                continue
            
            py_def = element.py_def
            if py_def is not None:
                # define macro
                subclauses = []
                subclauses.append(clauses.Method("_macro", py_def.args))
                subclauses.append(clauses.Visit(element))
                _.append(clauses.Group(subclauses))
                
                # assign to variable
                _.append(clauses.Define(
                    py_def.name, types.parts((types.value("_macro"),))))
                    
        # condition
        if self._condition is not None:
            _.append(clauses.Condition(self._condition))

        # repeat
        if self._repeat is not None:
            variables, expression = self._repeat
            if len(variables) != 1:
                raise ValueError(
                    "Cannot unpack more than one variable in a "
                    "repeat statement.")
            _.append(clauses.Repeat(variables[0], expression))

        # tag tail (deferred)
        if self.tail:
            _.append(clauses.Out(self.tail.encode('utf-8'), defer=True))

        # compute dynamic flag
        dynamic = (self._replace or
                   self._content or
                   self.i18n_translate is not None)
        
        # tag
        if self._replace is None:
            selfclosing = self.text is None and not dynamic and len(self) == 0
            tag = clauses.Tag(self.tag, self._get_attributes(),
                              expression=self.py_attrs, selfclosing=selfclosing)

            if self._omit:
                _.append(clauses.Condition(_not(self._omit), [tag],
                                           finalize=False))
            elif self._omit is not None:
                pass
            else:
                _.append(tag)

        # tag text (if we're not replacing tag body)
        if self.text and not dynamic:
            _.append(clauses.Out(self.text.encode('utf-8')))

        # dynamic content and content translation
        replace = self._replace
        content = self._content

        if replace and content:
            raise ValueError("Can't use replace clause together with "
                             "content clause.")

        expression = replace or content
        if expression:
            if self.i18n_translate is not None:
                if self.i18n_translate != "":
                    raise ValueError("Can't use message id with "
                                     "dynamic content translation.")
                _.append(clauses.Translate())

            _.append(clauses.Write(expression))
        else:
            if self.i18n_translate is not None:
                msgid = self.i18n_translate
                if not msgid:
                    msgid = self._msgid()

                # for each named block, create a new output stream
                # and use the value in the translation mapping dict
                elements = [e for e in self if e.i18n_name]

                if elements:
                    mapping = '_mapping'
                    _.append(clauses.Assign(types.value('{}'), mapping))
                else:
                    mapping = 'None'
                    
                for element in elements:
                    name = element.i18n_name
                    
                    subclauses = []
                    subclauses.append(clauses.Define(
                        ('_out', '_write'),
                        types.value('generation.initialize_stream()')))
                    subclauses.append(clauses.Visit(element))
                    subclauses.append(clauses.Assign(
                        types.value('_out.getvalue()'),
                        "%s['%s']" % (mapping, name)))

                    _.append(clauses.Group(subclauses))

                _.append(clauses.Assign(
                    _translate(types.value(repr(msgid)), mapping=mapping,
                               default='_marker'), '_result'))

                # write translation to output if successful, otherwise
                # fallback to default rendition; 
                result = types.value('_result')
                condition = types.value('_result is not _marker')
                _.append(clauses.Condition(condition,
                            [clauses.UnicodeWrite(result)]))

                subclauses = []
                if self.text:
                    subclauses.append(clauses.Out(self.text.encode('utf-8')))
                for element in self:
                    name = element.i18n_name
                    if name:
                        value = types.value("%s['%s']" % (mapping, name))
                        subclauses.append(clauses.Write(value))
                    else:
                        subclauses.append(clauses.Out(
                            lxml.etree.tostring(element)))

                if subclauses:
                    _.append(clauses.Else(subclauses))

        return _

    def _wrap_comment(self, element):
        index = self.index(element)

        t = parser.makeelement(utils.tal_attr('comment'))
        t.attrib['omit-tag'] = ''
        t.tail = element.tail
        t.text = '<!--' + element.text + '-->'

        for child in element.getchildren():
            t.append(child)

        self.remove(element)
        self.insert(index, t)
        t.update()
    
    def _msgid(self):
        """Create an i18n msgid from the tag contents."""

        out = StringIO(self.text)
        for element in self:
            name = element.i18n_name
            if name:
                out.write("${%s}" % name)
                out.write(element.tail)
            else:
                out.write(lxml.etree.tostring(element))

        msgid = out.getvalue().strip()
        msgid = msgid.replace('  ', ' ').replace('\n', '')
        
        return msgid

    def _get_static_attributes(self):
        attributes = {}

        for key in self.keys():
            if not key.startswith('{'):
                attributes[key] = self.attrib[key]

        return attributes
        
    def _get_attributes(self):
        """Aggregate static, dynamic and translatable attributes."""

        # static attributes are at the bottom of the food chain
        attributes = self._get_static_attributes()
        
        # dynamic attributes
        attrs = self.tal_attributes
        if attrs is not None:
            for variables, expression in attrs:
                if len(variables) != 1:
                    raise ValueError("Tuple definitions in assignment clause "
                                     "is not supported.")

                variable = variables[0]
                attributes[variable] = expression
        else:
            attrs = []

        dynamic = [key for (key, expression) in attrs]

        # translated attributes
        if self.i18n_attributes:
            for variable, msgid in self.i18n_attributes:
                if msgid:
                    if variable in dynamic:
                        raise ValueError(
                            "Message id not allowed in conjunction with "
                            "a dynamic attribute.")

                    value = types.value('"%s"' % msgid)

                    if variable in attributes:
                        default = '"%s"' % attributes[variable]
                        expression = _translate(value, default=default)
                    else:
                        expression = _translate(value)
                else:
                    if variable in dynamic or variable in attributes:
                        text = '"%s"' % attributes[variable]
                        expression = _translate(text)
                    else:
                        raise ValueError("Must be either static or dynamic "
                                         "attribute when no message id "
                                         "is supplied.")

                attributes[variable] = expression

        return attributes

    def _pull_attribute(self, name, default=None):
        if name in self.attrib:
            value = self.attrib[name]
            del self.attrib[name]
            return value
        return default
    
    def _add_tal_define(self, variable, expression):
        name = utils.tal_attr('define')
        define = "%s %s; " % (variable, expression)

        if name in self.attrib:
            self.attrib[name] += define
        else:
            self.attrib[name] = define
    
    @property
    def _define(self):
        return self.tal_define or self.py_with

    @property
    def _condition(self):
        return self.tal_condition or self.py_if

    @property
    def _repeat(self):
        return self.tal_repeat or self.py_for

    @property
    def _replace(self):
        return self.tal_replace or self.py_replace

    @property
    def _content(self):
        return self.tal_content or self.py_content

    @property
    def _omit(self):
        if self.tal_omit is not None:
            return self.tal_omit
        return self.py_strip
    
    tal_define = utils.attribute(
        utils.tal_attr('define'), lambda p: p.definitions)
    tal_condition = utils.attribute(
        utils.tal_attr('condition'), lambda p: p.expression)
    tal_repeat = utils.attribute(
        utils.tal_attr('repeat'), lambda p: p.definition)
    tal_attributes = utils.attribute(
        utils.tal_attr('attributes'), lambda p: p.definitions)
    tal_content = utils.attribute(
        utils.tal_attr('content'), lambda p: p.output)
    tal_replace = utils.attribute(
        utils.tal_attr('replace'), lambda p: p.output)
    tal_omit = utils.attribute(
        utils.tal_attr('omit-tag'), lambda p: p.expression)
    tal_default_expression = utils.attribute(
        utils.tal_attr('default-expression'))
    i18n_translate = utils.attribute(
        utils.i18n_attr('translate'))
    i18n_attributes = utils.attribute(
        utils.i18n_attr('attributes'), lambda p: p.mapping)
    i18n_domain = utils.attribute(
        utils.i18n_attr('domain'))
    i18n_name = utils.attribute(
        utils.i18n_attr('name'))
    py_if = utils.attribute(
        utils.py_attr('if'), lambda p: p.expression)
    py_for = utils.attribute(
        utils.py_attr('for'), lambda p: p.definition)
    py_with = utils.attribute(
        utils.py_attr('with'), lambda p: expressions.PythonTranslation.definitions)
    py_choose = utils.attribute(
        utils.py_attr('choose'), lambda p: p.expression)
    py_when = utils.attribute(
        utils.py_attr('when'), lambda p: p.expression)
    py_match = utils.attribute(
        utils.py_attr('match'))
    py_def = utils.attribute(
        utils.py_attr('def'), lambda p: p.method)
    py_attrs = utils.attribute(
        utils.py_attr('attrs'), lambda p: p.expression)
    py_content = utils.attribute(
        utils.py_attr('content'), lambda p: p.output)
    py_replace = utils.attribute(
        utils.py_attr('replace'), lambda p: p.output)
    py_strip = utils.attribute(
        utils.py_attr('strip'), lambda p: p.expression)
    
class TALElement(Element):
    tal_define = utils.attribute("define", lambda p: p.definitions)
    tal_condition = utils.attribute("condition", lambda p: p.expression)
    tal_replace = utils.attribute("replace", lambda p: p.output)
    tal_repeat = utils.attribute("repeat", lambda p: p.definition)
    tal_attributes = utils.attribute("attributes", lambda p: p.expression)
    tal_content = utils.attribute("content", lambda p: p.output)
    tal_omit = utils.attribute("omit-tag", lambda p: p.expression, u"")
    tal_default_expression = utils.attribute("default-expression", lambda p: p.name)
    
    def _get_static_attributes(self):
        attributes = {}

        for key in self.keys():
            if key not in ('define',
                           'condition',
                           'replace',
                           'repeat',
                           'attributes',
                           'content',
                           'omit-tag'):
                raise ValueError(
                    u"Attribute '%s' not allowed in the namespace '%s'" %
                    (key, self.nsmap[self.prefix]))

        return attributes

class PyElement(Element):
    tal_omit = utils.attribute("omit-tag", lambda p: p.expression, u"")

class PyIfElement(PyElement):
    py_if = utils.attribute("test", lambda p: p.expression)

class PyForElement(PyElement):
    py_for = utils.attribute("each", lambda p: p.definition)

class PyWithElement(PyElement):
    py_with = utils.attribute(
        "vars", lambda p: expressions.PythonTranslation.definitions)

class PyDefElement(PyElement):
    py_def = utils.attribute("function", lambda p: p.method)

class PyMatchElement(PyElement):
    py_match = utils.attribute("path")

# set up namespaces for XML parsing
lookup = lxml.etree.ElementNamespaceClassLookup()
parser = lxml.etree.XMLParser()
parser.setElementClassLookup(lookup)

try:
    ns_lookup = lookup.get_namespace
except AttributeError:
    ns_lookup = lxml.etree.Namespace
    
ns_lookup(config.XML_NS)[None] = Element
ns_lookup(config.TAL_NS)[None] = TALElement
ns_lookup(config.PY_NS)["if"] = PyIfElement
ns_lookup(config.PY_NS)["for"] = PyForElement
ns_lookup(config.PY_NS)["def"] = PyDefElement
ns_lookup(config.PY_NS)["with"] = PyWithElement
ns_lookup(config.PY_NS)["match"] = PyMatchElement

def translate_xml(body, *args, **kwargs):
    tree = lxml.etree.parse(StringIO(body), parser)
    root = tree.getroot()
    return translate_etree(root, *args, **kwargs)

def translate_etree(root, params=[], default_expression='python'):
    if None not in root.nsmap:
        raise ValueError, "Must set default namespace."

    # set default expression name
    key = utils.tal_attr('default-expression')
    if key not in root.attrib:
        root.attrib[key] = default_expression

    # set up code generation stream
    generator = generation.Generator(params)
    stream = generator.stream

    # output doctype if any
    tree = root.getroottree()
    if tree.docinfo.doctype:
        dt = (tree.docinfo.doctype +'\n').encode('utf-8')
        doctype = clauses.Out(dt)
        stream.scope.append(set())
        stream.begin([doctype])
        stream.end([doctype])
        stream.scope.pop()

    root.start(stream)

    return generator

def translate_text(body, *args, **kwargs):
    xml = parser.makeelement(
        utils.xml_attr('text'), nsmap={None: config.XML_NS})
    xml.text = body
    xml.attrib[utils.tal_attr('omit-tag')] = ''
    return translate_etree(xml, *args, **kwargs)
    
def _translate(value, mapping=None, default=None):
    format = ("_translate(%s, domain=_domain, mapping=%s, context=_context, "
              "target_language=_target_language, default=%s)")
    return types.value(format % (value, mapping, default))

def _not(value):
    return types.value("not (%s)" % value)
