# -*- coding: utf-8 -*-
#
# Copyright (c) 2007 - 2009 -- Lars Heuer - Semagia <http://www.semagia.com/>.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#
#     * Redistributions in binary form must reproduce the above
#       copyright notice, this list of conditions and the following
#       disclaimer in the documentation and/or other materials provided
#       with the distribution.
#
#     * Neither the project name nor the names of the contributors may be 
#       used to endorse or promote products derived from this software 
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
"""\
JSON Topic Maps (JTM) 1.0.

:author:       Lars Heuer (heuer[at]semagia.com)
:organization: Semagia - http://www.semagia.com/
:version:      $Rev: 169 $ - $Date: 2009-06-26 14:44:17 +0200 (Fr, 26 Jun 2009) $
:license:      BSD license
"""
from urllib import urlopen
import codecs
from tm.mio import MIOException
from tm.mio.deserializer import Deserializer, Context

__all__ = ['create_deserializer']

def create_deserializer(**kw): #pylint: disable-msg=W0613
    """\
    
    """
    return JTMDeserializer()

def make_lexer(data):
    from mio.reader.jtm import lexer #pylint: disable-msg=E0611
    return lexer.Lexer(data)

def make_parser(source, lexer):
    from mio.reader.jtm.parser import JTMParser #pylint: disable-msg=E0611
    return JTMParser(source.iri, lexer, encoding=source.encoding or 'utf-8')

class JTMDeserializer(Deserializer):

    version = '1.0'

    def __init__(self):
        super(JTMDeserializer, self).__init__()

    def _do_parse(self, source):
        data = source.stream
        if not data:
            try:
                data = urlopen(source.iri)
            except IOError:
                raise MIOException('Cannot read from ' + source.iri)
        parser = make_parser(source, make_lexer(self._reader(data, source.encoding)))
        parser.parse(self.handler)

    def _reader(self, fileobj, encoding=None):
        return codecs.getreader(encoding or 'utf-8')(fileobj).read()
