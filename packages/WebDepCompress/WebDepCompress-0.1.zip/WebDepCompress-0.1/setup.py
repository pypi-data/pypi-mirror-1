from setuptools import setup


setup(
    name='WebDepCompress',
    version='0.1',
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
    '''
)
