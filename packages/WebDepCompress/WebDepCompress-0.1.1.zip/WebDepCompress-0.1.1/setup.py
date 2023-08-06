"""
    webdepcompress
    ~~~~~~~~~~~~~~

    This package implements a simple framework-independent system for web
    dependency compression.  With the help of various compresseors it
    compresses JavaScript and CSS if necessary and allows a fallback if
    the files are used uncompressed (developer mode).

    For more information have a look at the docstring.
"""
from setuptools import setup


setup(
    name='WebDepCompress',
    version='0.1.1',
    url='http://dev.pocoo.org/hg/webdepcompress/',
    license='BSD',
    author='Armin Ronacher',
    author_email='armin.ronacher@active-4.com',
    description='JavaScript and CSS Compression Package',
    long_description=__doc__,
    packages=['webdepcompress', 'webdepcompress.compressors'],
    namespace_packages=['webdepcompress', 'webdepcompress.compressors'],
    platforms='any',
    entry_points='''
    [distutils.commands]
    compress_deps = webdepcompress.support:compress_deps

    [distutils.setup_keywords]
    webdepcompress_manager = webdepcompress.support:get_webdepcompress_manager

    [webdepcompress.compressors]
    naive = webdepcompress.compressors.naive:NaiveCompressor
    ''',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
