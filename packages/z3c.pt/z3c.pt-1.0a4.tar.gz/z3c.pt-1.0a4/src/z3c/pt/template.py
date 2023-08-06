import os
import macro
import config
import filecache
import translation

class BaseTemplate(object):
    """Constructs a template object using the template language
    defined by ``parser`` (``ZopePageTemplateParser`` or
    ``GenshiParser`` as of this writing). Must be passed an input
    string as ``body``. The ``format`` parameter supports values 'xml'
    and 'text'."""

    compilers = {
        'xml': translation.Compiler,
        'text': translation.Compiler.from_text}

    format = 'xml'
    
    def __init__(self, body, parser, format=None):
        self.body = body
        self.parser = parser        
        self.signature = hash(body)
        self.registry = {}
        if format is not None:
            self.format = format
            
    @property
    def translate(self):
        return NotImplementedError("Must be provided by subclass.")

    @property
    def macros(self):
        return macro.Macros(self.render)

    @property
    def compiler(self):
        return self.compilers[self.format](self.body, self.parser)
    
    def cook(self, **kwargs):
        return self.compiler(**kwargs)
    
    def cook_check(self, macro, params):
        key = self.signature, macro, params
        template = self.registry.get(key, None)
        if template is None:
            template = self.cook(macro=macro, params=params)
            self.registry[key] = template
            
        return template

    def prepare(self, kwargs):
        pass
    
    def render(self, macro=None, **kwargs):
        self.prepare(kwargs)
        template = self.cook_check(macro, tuple(kwargs))
        kwargs.update(template.selectors)
        return template.render(**kwargs)

    def __repr__(self):
        return u"<%s %d>" % (self.__class__.__name__, id(self))

    __call__ = render
    
class BaseTemplateFile(BaseTemplate):
    """Constructs a template object using the template language
    defined by ``parser``. Must be passed an absolute (or
    current-working-directory-relative) filename as ``filename``. If
    ``auto_reload`` is true, each time the template is rendered, it
    will be recompiled if it has been changed since the last
    rendering."""
    
    global_registry = {}
    
    def __init__(self, filename, parser, format=None, auto_reload=False):
        BaseTemplate.__init__(
            self, None, parser, format=format)

        self.auto_reload = auto_reload
        self.filename = filename = os.path.abspath(
            os.path.normpath(os.path.expanduser(filename)))

        # make sure file exists
        os.lstat(filename)

        # read template
        self.read()

        # persist template registry on disk
        if config.DISK_CACHE:
            self.registry = self.global_registry.setdefault(
                filename, filecache.TemplateCache(filename))

        self.xincludes = XIncludes(
            self.global_registry, os.path.dirname(filename), self.clone)
        
    def clone(self, filename, format=None):
        cls = type(self)
        return cls(filename, self.parser, format=format)
        
    def _get_filename(self):
        return getattr(self, '_filename', None)

    def _set_filename(self, filename):
        self._filename = filename
        self._v_last_read = False

    filename = property(_get_filename, _set_filename)

    def read(self):
        fd = open(self.filename, 'r')
        self.body = body = fd.read()
        fd.close()
        self.signature = hash(body)
        self._v_last_read = self.mtime()

    def cook_check(self, *args):
        if self.auto_reload and self._v_last_read != self.mtime():
            self.read()

        return BaseTemplate.cook_check(self, *args)

    def prepare(self, kwargs):
        kwargs[config.SYMBOLS.xincludes] = self.xincludes

    def mtime(self):
        try:
            return os.path.getmtime(self.filename)
        except (IOError, OSError):
            return 0

    def __repr__(self):
        return u"<%s %s>" % (self.__class__.__name__, self.filename)

class XIncludes(object):
    """Dynamic XInclude registry providing a ``get``-method that will
    resolve a filename to a template instance. Format must be
    explicitly provided."""
    
    def __init__(self, registry, relpath, factory):
        self.registry = registry
        self.relpath = relpath
        self.factory = factory

    def get(self, filename, format):
        if not os.path.isabs(filename):
            filename = os.path.join(self.relpath, filename)        
        template = self.registry.get(filename)
        if template is not None:
            return template
        return self.factory(filename, format=format)
    
