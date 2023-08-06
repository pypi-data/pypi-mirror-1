# -*- coding: utf-8 -*-
"""
    webdepcompress.support
    ~~~~~~~~~~~~~~~~~~~~~~

    Hooks webdepcompress into other tools such as distutils.

    :copyright: (c) 2009 by Armin Ronacher, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""
from webdepcompress.manager import PackManager, import_string

from distutils import log
from distutils.errors import DistutilsSetupError
from distutils.cmd import Command


class compress_deps(Command):
    """A distutils command for dep compression."""

    description = 'Compresses web dependencies'
    user_options = [
        ('clean', None, 'removes the compressed files'),
        ('compressor', 'c', 'the compressor to use (defaults to auto)')
    ]
    boolean_options = ['clean']

    def initialize_options(self):
        self.clean = False
        self.compressor = 'auto'

    def finalize_options(self):
        pass

    def run(self):
        mgr = self.distribution.webdepcompress_manager
        if self.clean:
            print 'Remove compressed files'
            mgr.remove_compressed()
        else:
            mgr.compress(log=log)


def get_webdepcompress_manager(dist, name, value):
    """Check the webdep manager argument to setup()"""
    assert name == 'webdepcompress_manager'
    mgr = import_string(value, silent=True)
    if mgr is None:
        raise DistutilsSetupError('webdepcompress manager not found')
    dist.webdepcompress_manager = mgr
