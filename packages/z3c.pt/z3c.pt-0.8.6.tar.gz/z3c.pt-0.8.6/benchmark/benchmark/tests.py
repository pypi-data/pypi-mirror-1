import os
import unittest
import time
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

import zope.component.testing
import zope.configuration.xmlconfig

import zope.pagetemplate.pagetemplatefile
import z3c.pt
from z3c.pt import generation

def benchmark(title):
    def decorator(f):
        def wrapper(*args):
            print "==========================\n %s\n==========================" % title
            return f(*args)
        return wrapper
    return decorator

def timing(func, *args, **kwargs):
    t1 = t2 = time.time()
    i = 0
    while t2 - t1 < 3:
        func(*args, **kwargs)
        i += 1
        t2 = time.time()
    return 100*(t2-t1)/i

class BaseTestCase(unittest.TestCase):

    table = [dict(a=1,b=2,c=3,d=4,e=5,f=6,g=7,h=8,i=9,j=10) \
             for x in range(1000)]

    def setUp(suite):
        zope.component.testing.setUp(suite)
        zope.configuration.xmlconfig.XMLConfig('configure.zcml', z3c.pt)()

    def tearDown(suite):
        zope.component.testing.tearDown(suite)

class BenchmarkTestCase(BaseTestCase):

    helloworld_z3c = z3c.pt.PageTemplate("""\
    <div xmlns="http://www.w3.org/1999/xhtml">
    Hello World!
    </div>""")

    helloworld_zope = zope.pagetemplate.pagetemplate.PageTemplate()
    helloworld_zope.pt_edit("""\
    <div xmlns="http://www.w3.org/1999/xhtml">
    Hello World!
    </div>""", 'text/xhtml')
    
    bigtable_python_z3c = z3c.pt.PageTemplate("""\
    <table xmlns="http://www.w3.org/1999/xhtml"
    xmlns:tal="http://xml.zope.org/namespaces/tal">
    <tr tal:repeat="row table">
    <td tal:repeat="c row.values()">
    <span tal:define="d c + 1"
    tal:attributes="class 'column-' + str(d)"
    tal:content="d" />
    </td>
    </tr>
    </table>""")

    bigtable_path_z3c = z3c.pt.PageTemplate("""\
    <table xmlns="http://www.w3.org/1999/xhtml"
    xmlns:tal="http://xml.zope.org/namespaces/tal"
    tal:default-expression="path">
    <tr tal:repeat="row table">
    <td tal:repeat="c row/values">
    <span tal:define="d python: c + 1"
    tal:attributes="class string:column-${d}"
    tal:content="d" />
    </td>
    </tr>
    </table>""")

    bigtable_python_zope = zope.pagetemplate.pagetemplate.PageTemplate()
    bigtable_python_zope.pt_edit("""\
    <table xmlns="http://www.w3.org/1999/xhtml"
    xmlns:tal="http://xml.zope.org/namespaces/tal">
    <tr tal:repeat="row python: options['table']">
    <td tal:repeat="c python: row.values()">
    <span tal:define="d python: c + 1"
    tal:attributes="class python:'column-'+str(d)"
    tal:content="d" />
    </td>
    </tr>
    </table>""", 'text/xhtml')

    bigtable_path_zope = zope.pagetemplate.pagetemplate.PageTemplate()
    bigtable_path_zope.pt_edit("""\
    <table xmlns="http://www.w3.org/1999/xhtml"
    xmlns:tal="http://xml.zope.org/namespaces/tal">
    <tr tal:repeat="row options/table">
    <td tal:repeat="c row/values">
    <span tal:define="d python: c + 1"
    tal:attributes="class string:column-${d}"
    tal:content="d" />
    </td>
    </tr>
    </table>""", 'text/xhtml')

    @benchmark(u"Hello World")
    def testHelloWorld(self):
        t_z3c = timing(self.helloworld_z3c)
        t_zope = timing(self.helloworld_zope)

        print "z3c.pt:            %.2f" % t_z3c
        print "zope.pagetemplate: %.2f" % t_zope
        print "                   %.2fX" % (t_zope/t_z3c)

    @benchmark(u"Big table (python)")
    def testBigTablePython(self):
        table = self.table

        t_z3c = timing(self.bigtable_python_z3c, table=table)
        t_zope = timing(self.bigtable_python_zope, table=table)

        print "z3c.pt:            %.2f" % t_z3c
        print "zope.pagetemplate: %.2f" % t_zope
        print "                   %.2fX" % (t_zope/t_z3c)

    @benchmark(u"Big table (path)")
    def testBigTablePath(self):
        table = self.table

        t_z3c = timing(self.bigtable_path_z3c, table=table, request=object())
        t_zope = timing(self.bigtable_path_zope, table=table)

        print "z3c.pt:            %.2f" % t_z3c
        print "zope.pagetemplate: %.2f" % t_zope
        print "                   %.2fX" % (t_zope/t_z3c)

    @benchmark(u"Compilation")
    def testCompilation(self):
        table = self.table

        t_z3c = timing(self.bigtable_python_z3c.cook, ['table'])
        t_zope = timing(self.bigtable_python_zope._cook)

        print "z3c.pt:            %.2f" % t_z3c
        print "zope.pagetemplate: %.2f" % t_zope
        print "                   %.2fX" % (t_zope/t_z3c)


class FileBenchmarkTestCase(BaseTestCase):

    @benchmark(u"Big table (python) File")
    def testBigTablePythonFile(self):
        table = self.table

        files = os.path.abspath(os.path.join(__file__, '..', 'input'))
        def testfile(name):
            return os.path.join(files, name)

        z3cfile = z3c.pt.PageTemplateFile(
            testfile('bigtable_python_z3c.pt'))

        zopefile = zope.pagetemplate.pagetemplatefile.PageTemplateFile(
            testfile('bigtable_python_zope.pt'))

        t_z3c = timing(z3cfile.render, table=table)
        t_zope = timing(zopefile, table=table)

        print "z3c.pt:            %.2f" % t_z3c
        print "zope.pagetemplate: %.2f" % t_zope
        print "                   %.2fX" % (t_zope/t_z3c)

    @benchmark(u"Big table (path) File")
    def testBigTablePathFile(self):
        table = self.table

        files = os.path.abspath(os.path.join(__file__, '..', 'input'))
        def testfile(name):
            return os.path.join(files, name)

        z3cfile = z3c.pt.PageTemplateFile(
            testfile('bigtable_path_z3c.pt'))

        zopefile = zope.pagetemplate.pagetemplatefile.PageTemplateFile(
            testfile('bigtable_path_zope.pt'))

        t_z3c = timing(z3cfile.render, table=table, request=object())
        t_zope = timing(zopefile, table=table, request=object())

        print "z3c.pt:            %.2f" % t_z3c
        print "zope.pagetemplate: %.2f" % t_zope
        print "                   %.2fX" % (t_zope/t_z3c)

# Use a custom context to add real i18n lookup

from zope.i18n import translate
from zope.i18n.interfaces import INegotiator
from zope.i18n.interfaces import ITranslationDomain
from zope.i18n.negotiator import Negotiator
from zope.i18n.simpletranslationdomain import SimpleTranslationDomain
from zope.i18n.tests.test_negotiator import Env
from zope.tales.tales import Context

class ZopeI18NContext(Context):

    def translate(self, msgid, domain=None, context=None,
                  mapping=None, default=None):
        context = self.vars['options']['env']
        return translate(msgid, domain, mapping,
                         context=context, default=default)

def _getContext(self, contexts=None, **kwcontexts):
    if contexts is not None:
        if kwcontexts:
            kwcontexts.update(contexts)
        else:
            kwcontexts = contexts
    return ZopeI18NContext(self, kwcontexts)

def _pt_getEngineContext(namespace):
    self = namespace['template']
    engine = self.pt_getEngine()
    return _getContext(engine, namespace)


class I18NBenchmarkTestCase(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)
        self.env = Env(('da', 'en', 'fr', 'no'))
        zope.component.provideUtility(Negotiator(), INegotiator)
        catalog = SimpleTranslationDomain('domain')
        zope.component.provideUtility(catalog, ITranslationDomain, 'domain')
        self.files = os.path.abspath(os.path.join(__file__, '..', 'input'))
        self.disable = generation.DISABLE_I18N

    def tearDown(self):
        BaseTestCase.tearDown(self)
        generation.DISABLE_I18N = self.disable

    def _testfile(self, name):
        return os.path.join(self.files, name)

    @benchmark(u"Internationalization")
    def testI18N(self):
        table = self.table

        z3cfile = z3c.pt.PageTemplateFile(
            self._testfile('bigtable_i18n_z3c.pt'))

        zopefile = zope.pagetemplate.pagetemplatefile.PageTemplateFile(
            self._testfile('bigtable_i18n_zope.pt'))

        # In order to have a fair comparision, we need real zope.i18n handling
        zopefile.pt_getEngineContext = _pt_getEngineContext

        t_z3c = timing(z3cfile, table=table, _context=self.env)
        t_zope = timing(zopefile, table=table, env=self.env)

        print "z3c.pt:            %.2f" % t_z3c
        print "zope.pagetemplate: %.2f" % t_zope
        print "                   %.2fX" % (t_zope/t_z3c)

    @benchmark(u"I18N (disabled)")
    def testDisabledI18N(self):
        table = self.table

        z3cfile = z3c.pt.PageTemplateFile(
            self._testfile('bigtable_i18n_z3c.pt'))

        zopefile = zope.pagetemplate.pagetemplatefile.PageTemplateFile(
            self._testfile('bigtable_i18n_zope.pt'))

        zopefile.pt_getEngineContext = _pt_getEngineContext

        # Let's disable i18n for this test
        generation.DISABLE_I18N = True

        t_z3c = timing(z3cfile, table=table, _context=self.env)
        t_zope = timing(zopefile, table=table, env=self.env)

        print "z3c.pt:            %.2f" % t_z3c
        print "zope.pagetemplate: %.2f" % t_zope
        print "                   %.2fX" % (t_zope/t_z3c)

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(BenchmarkTestCase),
        unittest.makeSuite(FileBenchmarkTestCase),
        unittest.makeSuite(I18NBenchmarkTestCase),
        ))

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")

