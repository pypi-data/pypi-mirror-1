# -*- coding: utf-8 -*-
"""
    webdepcompress
    ~~~~~~~~~~~~~~

    This package implements a simple framework-independent system for web
    dependency compression.  With the help of various compresseors it
    compresses JavaScript and CSS if necessary and allows a fallback if
    the files are used uncompressed (developer mode).

    This package provides a naive, whitespace removing compressor for
    CSS and JavaScript but a powerful, yuicompressor based compressing
    algorithm can be installed from the pypi that is used automatically
    if available.  This makes it possible to ship this package with an
    application for production usage and precompressed files without
    having to install yuicompressor and Java.

    Declaring Packs
    ---------------

    Add a file to your package (for example packs.py) with the following
    contents::

        from webdepcompress import PackManager

        mgr = PackManager(os.path.join(os.path.dirname(__file__), 'static'),
                          lambda fn, t: '/static/' + fn)

        mgr.add_pack('default', ['style.css', 'print.css',
                                 'jquery.js', 'application.js'])

    First you have to create a pack manager.  That manager keeps a registry
    of all your packs, because you can have multiple of those.  The first
    argument to it is the path to where the files are stored.  Most of the
    time it makes sure to point to somewhere inside your package.  That path
    is used as base path for the source files and it will also be used as
    a path for the compressed files when created.  If you want a different
    path for the generated files, you can do so.  Have a look at the
    :cls:`PackManager` documentation for more information.

    The second argument to the manager is a function that returns the URL
    to the file.  In this case it assumes that the files are available
    as ``/static/filename.css`` and so forth.

    When you add a pack you call :meth:`~PackManager.add_pack` with the
    name of the pack as first argument and the files it should pack together
    as the second.

    Using Packs
    -----------

    Packs provide a simple interface:

    >>> mgr['default']
    <Pack 'default'>
    >>> print mgr['default']
    <link rel="stylesheet" type="text/css" href="/static/style.css">
    <link rel="stylesheet" type="text/css" href="/static/print.css">
    <script type="text/javascript" src="/static/jquery.js"></script>
    <script type="text/javascript" src="/static/application.js"></script>

    As you can see, the `__str__` and `__unicode__` special methods of a
    pack return the HTML needed to include the files specified.  Please note
    that it will print out the stylesheets before the scripts by default
    and that scripts and files are kept in the order specified but grouped
    by type.  It also outputs HTML4/HTML5 by default and not XHTML.  This
    can be changed.

    Packs can be compressed by calling the :meth:`~PackManager.compress`
    method on the manager or of a pack:

    >>> mgr.compress()

    That can take a while, after that you can see that the manager spits
    out the compressed includes:

    >>> print mgr['default']
    <link rel="stylesheet" type="text/css" href="/static/default.compressed.css">
    <script type="text/javascript" src="/static/default.compressed.js"></script>

    You can pass packs to your template engine easily.  The best idea is to
    forward the pack as a string or list of strings so that the template
    cannot call `compress` on it.

    Setuputils Integration
    ----------------------

    If you add a webdepcompress_manager setting to your setup call you
    can use the `compress_deps` command from `setup.py`:

        setup(
            ...,
            webdepcompress_manager='yourapplication.packs.mgr'
        )

    Then you can compile the deps from the command line::

        $ python setup.py compress_deps

    And clean the compressed files again::

        $ python setup.py compress_deps --clean


    :copyright: (c) 2009 by Armin Ronacher, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""
from manager import PackManager
__import__('pkg_resources').declare_namespace(__name__)
