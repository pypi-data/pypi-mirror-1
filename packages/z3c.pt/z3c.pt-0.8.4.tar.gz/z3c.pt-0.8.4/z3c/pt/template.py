import os
import sys
import codegen
import traceback

class BaseTemplate(object):
    registry = {}
    default_expression = 'python'
    
    def __init__(self, body, default_expression=None):
        self.body = body
        self.signature = hash(body)        

        if default_expression:
            self.default_expression = default_expression
            
    @property
    def translate(self):
        return NotImplementedError("Must be implemented by subclass.")

    def cook(self, params):
        generator = self.translate(
            self.body, params=params, default_expression=self.default_expression)
        
        source, _globals = generator()
         
        suite = codegen.Suite(source)
        
        self.source = source
        self.annotations = generator.stream.annotations
        
        _globals.update(suite._globals)
        _locals = {}

        exec suite.code in _globals, _locals

        return _locals['render']

    def render(self, **kwargs):
        signature = self.signature + hash(",".join(kwargs.keys()))

        template = self.registry.get(signature)
        if not template:
            self.registry[signature] = template = self.cook(kwargs.keys())

        try:
            return template(**kwargs)
        except Exception, e:
            __traceback_info__ = getattr(e, '__traceback_info__', None)
            if __traceback_info__ is not None:
                raise e
            
            etype, value, tb = sys.exc_info()
            lineno = tb.tb_next.tb_lineno-1
            annotations = self.annotations

            while lineno >= 0:
                if lineno in annotations:
                    annotation = annotations.get(lineno)
                    break

                lineno -= 1
            else:
                annotation = "n/a"

            e.__traceback_info__ = "While rendering %s, an exception was "\
                                   "raised evaluating ``%s``:\n\n" % \
                                   (repr(self), str(annotation))
            
            e.__traceback_info__ += "".join(traceback.format_tb(tb))
            
            raise e            
        
    def __call__(self, **kwargs):
        return self.render(**kwargs)

    def __repr__(self):
        return u"<%s %d>" % (self.__class__.__name__, id(self))

class BaseTemplateFile(BaseTemplate):
    def __init__(self, filename):
        if not os.path.isabs(filename):
            package_name = sys._getframe(2).f_globals['__name__']
            module = sys.modules[package_name]
            try:
                path = module.__path__[0]
            except AttributeError:
                path = module.__file__
                path = path[:path.rfind(os.sep)]
                
            filename = path + os.sep + filename

        # make sure file exists
        os.lstat(filename)
        self.filename = filename
                
    def _get_filename(self):
        return getattr(self, '_filename', None)

    def _set_filename(self, filename):
        self._filename = filename
        self._v_last_read = False

    filename = property(_get_filename, _set_filename)

    def render(self, **kwargs):
        if self._cook_check():
            self.body = open(self.filename, 'r').read()
            self.signature = hash(self.body)
            self._v_last_read = self.mtime()

        return BaseTemplate.render(self, **kwargs)
            
    def _cook_check(self):
        if self._v_last_read and not __debug__:
            return

        if self.mtime() == self._v_last_read:
            return

        return True

    def mtime(self):
        try:
            return os.path.getmtime(self.filename)
        except OSError:
            return 0

    def __repr__(self):
        return u"<%s %s>" % (self.__class__.__name__, self.filename)
