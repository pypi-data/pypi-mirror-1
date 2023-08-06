# -*- coding: utf-8 -*-
"""
    webdepcompress.manager
    ~~~~~~~~~~~~~~~~~~~~~~

    Implements the pack manager.

    :copyright: (c) 2009 by Armin Ronacher, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""
import os
from weakref import ref as weakref


CSS_TEMPLATE = '<link rel="stylesheet" type="text/css" href="%s">'
JS_TEMPLATE = '<script type="text/javascript" src="%s"></script>'
DEFAULT_COMPRESSORS = ('yui', 'naive')
GROUP_NAME = 'webdepcompress.compressors'


def import_string(import_name, silent=False):
    """Imports an object based on a string.  This is useful if you want to
    use import paths as endpoints or something similar.  An import path can
    be specified either in dotted notation (``xml.sax.saxutils.escape``)
    or with a colon as object delimiter (``xml.sax.saxutils:escape``).

    If `silent` is True the return value will be `None` if the import fails.

    :param import_name: the dotted name for the object to import.
    :param silent: if set to `True` import errors are ignored and
                   `None` is returned instead.
    :return: imported object
    """
    try:
        if ':' in import_name:
            module, obj = import_name.split(':', 1)
        elif '.' in import_name:
            module, obj = import_name.rsplit('.', 1)
        else:
            return __import__(import_name)
        return getattr(__import__(module, None, None, [obj]), obj)
    except (ImportError, AttributeError):
        if not silent:
            raise


def get_compressor(choices=None):
    """Return a suitable compressor from the choices or the builtins."""
    from pkg_resources import working_set

    if choices is None:
        choices = DEFAULT_COMPRESSORS
    for impname in choices:
        if '.' not in impname and ':' not in impname:
            for entry_point in working_set.iter_entry_points(GROUP_NAME, impname):
                return entry_point.load(require=True)
        else:
            compressor = import_string(impname, silent=True)
            if compressor is not None:
                return compressor

    raise RuntimeError('none of the specified compressors were found')


class Pack(object):
    """Represents a pack."""

    def __init__(self, mgr, name, files):
        self._mgr = weakref(mgr)
        self.name = name
        self._css = []
        self._js = []
        for filename in files:
            assert '.' in filename, 'unknown file without extension'
            ext = filename.rsplit('.', 1)[-1]
            if ext == 'js':
                self._js.append(filename)
            elif ext == 'css':
                self._css.append(filename)
            else:
                assert False, 'unknown extension ".%s"' % ext

    def get_mgr(self):
        rv = self._mgr()
        if rv is None:
            raise RuntimeError('manager got garbage collected')
        return rv

    def _compressed_filename(self, ext):
        return self.get_mgr().build_filename % {'name': self.name, 'ext': ext}

    def _make_gen_iterator(ext):
        def iter_ext(self):
            mgr = self.get_mgr()
            def _format(link):
                return getattr(mgr, ext + '_template') % mgr.link_func(link, ext)
            fn = self._compressed_filename(ext)
            if os.path.isfile(os.path.join(mgr.directory, fn)):
                yield _format(fn)
                return
            for filename in getattr(self, '_' + ext):
                yield _format(filename)
        return iter_ext

    iter_css = _make_gen_iterator('css')
    iter_js = _make_gen_iterator('js')
    del _make_gen_iterator

    def compress(self, compressors=None, log=None):
        mgr = self.get_mgr()
        compressor = get_compressor(compressors)(mgr, log)
        for ext in 'css', 'js':
            files = getattr(self, '_' + ext)
            if not files:
                continue
            filename = self._compressed_filename(ext)
            dst = open(os.path.join(mgr.directory, filename), 'w')
            try:
                getattr(compressor, 'compress_' + ext)(dst, files)
            finally:
                dst.close()

    def remove_compressed(self):
        mgr = self.get_mgr()
        for ext in 'css', 'js':
            filename = os.path.join(mgr.directory, self._compressed_filename(ext))
            if os.path.isfile(filename):
                os.remove(filename)

    def __iter__(self):
        mgr = self.get_mgr()
        iters = self.iter_css, self.iter_js
        if not mgr.css_first:
            iters = reversed(iters)
        for func in iters:
            for item in func():
                yield item

    def __unicode__(self):
        return u'\n'.join(self)

    def __str__(self):
        return '\n'.join(x.encode('utf-8') for x in self)


class PackManager(object):

    def __init__(self, directory, link_func, css_first=True,
                 css_template=CSS_TEMPLATE, js_template=JS_TEMPLATE,
                 build_filename='%(name)s.compressed.%(ext)s',
                 charset='utf-8'):
        self.directory = directory
        self.link_func = link_func
        self.css_first = css_first
        self.css_template = CSS_TEMPLATE
        self.js_template = JS_TEMPLATE
        self.build_filename = build_filename
        self.charset = charset
        self._packs = {}

    def compress(self, compressors=None, log=None):
        for pack in self._packs.itervalues():
            pack.compress(compressors, log)

    def remove_compressed(self):
        for pack in self._packs.itervalues():
            pack.remove_compressed()

    def add_pack(self, name, files):
        self._packs[name] = Pack(self, name, files)

    def remove_pack(self, name):
        rv = self._packs.pop(name, None)
        if rv is None:
            raise ValueError('no pack named %r found' % name)

    def __getitem__(self, name):
        return self._packs[name]
