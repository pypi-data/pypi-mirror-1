#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


r"""
iconv_codec: module to register codecs to encode/decode any char supported by 
system's iconv command.

Usage:
   just use the encoding with the 'iconv:' prefix.
   Examples:
   
   >>> '\xa3\x85\xa2\xa3'.decode('iconv:CP284')
   u'test'
   >>> u'testing'.encode('iconv:CSEBCDICFISEA')
   '\xa3\x85\xa2\xa3\x89\x95\x87'

The module will look for iconv in the path. If you need a different iconv
location just set it:

iconv_codec.ICONV_EXECUTABLE = '/usr/local/bin/iconv'

TODO: Code can still be optimized for stream calls.
"""

import codecs
import subprocess
import os

ICONV_EXECUTABLE='iconv' #: change this to reflect your installation path

def get_supported_codecs():
    """
    Returns a list of iconv supported codecs
    """
    cmd = [ICONV_EXECUTABLE, '--list']
    iconv = subprocess.Popen(cmd, env={'LANG': 'C'}, 
                             stdout=subprocess.PIPE,
                             stdin=open(os.devnull, 'w+'),
                             stderr=open(os.devnull, 'w+'))
    return [line.strip('/') for line in iconv.communicate()[0].splitlines()]
    
def _run_iconv(from_codec, to_codec, extra_params=None):
    cmd = [ICONV_EXECUTABLE, '-f', from_codec, '-t', to_codec, '-s']
    if extra_params is not None:
        cmd.extend(extra_params)
    iconv = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                  stdin=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  env={'LANG': 'C'})
    return iconv    

def _iconv_factory(codec_name):
    codec_name = codec_name.lower()
    if codec_name.startswith('iconv:'):
        name = codec_name[6:]

        def iconvencode(input, errors='strict', encoding=name):
            extra = []
            if errors == 'ignore':
                extra.append('-c')
            elif errors != 'strict':
                raise NotImplementedError("%r error handling not implemented"
                                          " for codec %r" % (errors, encoding))

            _input = input.encode('utf-8')
            iconv = _run_iconv('utf-8', encoding, extra)
            output, error = iconv.communicate(_input)
            if error:
                error = error.splitlines()[0]
                raise UnicodeEncodeError(encoding, input, 0, len(input), error)
            return output, len(input)

        def iconvdecode(input, errors='strict', encoding=name):
            extra = []
            if errors == 'ignore':
                extra.append('-c')
            elif errors != 'strict':
                raise NotImplementedError('%r error handling not implemented' 
                                          ' for codec %r' % (errors, encoding))
            _input = str(input)
            iconv = _run_iconv(encoding, 'utf-8', extra)
            output, error = iconv.communicate(_input)
            if error:
                error = error.splitlines()[0]
                raise UnicodeDecodeError(encoding, input, 0, len(input), error)
            output = output.decode('utf-8')
            return output, len(input)

        class IncrementalEncoder(codecs.IncrementalEncoder):
            def encode(self, input, final=False):
                return iconvencode(input, self.errors)[0]

        class IncrementalDecoder(codecs.BufferedIncrementalDecoder):
            _buffer_decode = staticmethod(iconvdecode)

        class StreamWriter(codecs.StreamWriter):
            pass
        StreamWriter.encode = staticmethod(iconvencode)

        class StreamReader(codecs.StreamReader):
            pass
        StreamReader.decode = staticmethod(iconvdecode)

        return codecs.CodecInfo(
                name=codec_name,
                encode=iconvencode,
                decode=iconvdecode,
                incrementalencoder=IncrementalEncoder,
                incrementaldecoder=IncrementalDecoder,
                streamreader=StreamReader,
                streamwriter=StreamWriter,
            )

codecs.register(_iconv_factory)

if __name__ == '__main__':
    x = u'áéíóúççç'
    assert x == x.encode('iconv:utf-8').decode('iconv:utf-8')
    import doctest
    doctest.testmod()
