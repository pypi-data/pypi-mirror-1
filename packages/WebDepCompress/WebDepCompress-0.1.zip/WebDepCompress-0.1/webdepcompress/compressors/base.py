# -*- coding: utf-8 -*-
"""
    webdepcompress.compressors.base
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implements the compressor base.

    :copyright: (c) 2009 by Armin Ronacher, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""


class CompressorBase(object):

    def __init__(self, mgr, log):
        self.mgr = mgr
        self.log = log

    def compress_css(self, stream, files):
        pass

    def compress_js(self, stream, files):
        pass
