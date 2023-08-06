from distutils.core import setup

long_description = r"""\
This module will register GNU iconv supported codecs for usage inside python.

Usage:
   Just register the codec you want:

   >>> import iconv_codecs
   >>> iconv_codecs.register('ansi_x3.110-1983')
   
   Then you can use it:
   
   >>> u'testing'.encode('ansi_x3.110-1983')
   'testing'

   Alternatively you can use them without registering, by using the iconv prefix:

   >>> '\x87'.decode('iconv:CP860')
   u'\xe7'
   >>> u'testing'.encode('iconv:CSEBCDICFISEA')
   '\xa3\x85\xa2\xa3\x89\x95\x87'

   To register all python unsupported codecs, just call register() without
   parameters:
   
   >>> iconv_codecs.register()
   >>> u'\xe7'.encode('utf32')
   '\xff\xfe\x00\x00\xe7\x00\x00\x00'
   
   That will poll iconv for a list of codecs it supports and register the ones
   python doesn't support already.   
"""

setup(name='iconv_codecs', version='0.2a1', author='Clovis Fabricio',
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
