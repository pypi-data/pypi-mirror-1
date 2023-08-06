from distutils.core import setup


long_description = r"""\
iconv_codec: module to register codecs to encode/decode any char supported by 
system's iconv command.

The codecs are registered in python and are available on all python functions
that support an encoding parameter.

Usage:
   After importing the module, just use the encoding with the 'iconv:' prefix.
   Examples:
   
   >>> import iconv_codecs
   >>> '\xa3\x85\xa2\xa3'.decode('iconv:CP284')
   u'test'
   >>> u'testing'.encode('iconv:CSEBCDICFISEA')
   '\xa3\x85\xa2\xa3\x89\x95\x87'

"""

setup(name='iconv_codecs', version='0.1a1', author='Clovis Fabricio',
      author_email='nosklo at gmail dot com', 
      url='http://pythonlog.wordpress.com/2009/03/03/ajuste-a-agua-conforme-o-foobar/',
      maintainer='Clovis Fabricio', maintainer_email='nosklo at gmail dot com',
      description='Python module to register all supported iconv codecs',
      long_description=long_description,
      py_modules=['iconv_codecs'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Plugins',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Software Development :: Internationalization',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Text Processing :: Filters',
          'Topic :: Utilities',
          ]
    )
