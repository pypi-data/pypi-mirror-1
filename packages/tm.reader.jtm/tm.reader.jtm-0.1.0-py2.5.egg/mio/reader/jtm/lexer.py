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
JSON Topic Maps (JTM) 1.0 lexer.

This lexer is a limited JSON lexer which accepts just JSON Topic Maps.

:author:       Lars Heuer (heuer[at]semagia.com)
:organization: Semagia - http://www.semagia.com/
:version:      $Rev: 169 $ - $Date: 2009-06-26 14:44:17 +0200 (Fr, 26 Jun 2009) $
:license:      BSD license
"""
import re
from mio.reader.jtm import consts

_KEYWORDS = {
             '"version"': consts.KW_VERSION,
             '"item_type"': consts.KW_ITEM_TYPE,
             '"topics"': consts.KW_TOPICS,
             '"associations"': consts.KW_ASSOCIATIONS,
             '"roles"': consts.KW_ROLES,
             '"occurrences"': consts.KW_OCCURRENCES,
             '"names"': consts.KW_NAMES,
             '"variants"': consts.KW_VARIANTS,
             '"scope"': consts.KW_SCOPE,
             '"type"': consts.KW_TYPE,
             '"player"': consts.KW_PLAYER,
             '"value"': consts.KW_VALUE,
             '"datatype"': consts.KW_DATATYPE,
             '"reifier"': consts.KW_REIFIER,
             '"parent"': consts.KW_PARENT,
             '"item_identifiers"': consts.KW_IIDS,
             '"subject_identifiers"': consts.KW_SIDS,
             '"subject_locators"': consts.KW_SLOS,
             }

_IGNORE = re.compile(r'\s+|(?:\s*,\s*)|(?:\s*:\s*)').match
_STRING = re.compile(r'"([^\\"]|(\\[\\"rntu/]))*"').match

class Lexer(object):
    
    def __init__(self, data):
        self._pos = 0
        self._data = data
        self._len = len(data)
        self._value = None

    def value(self):
        return self._value
    
    def token(self):
        if self._pos >= self._len:
            return None
        self._eat()
        self._value = None
        ch = self._data[self._pos]
        if ch == '{':
            self._pos+=1
            return consts.START_OBJECT
        elif ch == '}':
            self._pos+=1
            return consts.END_OBJECT
        elif ch == '[':
            self._pos+=1
            return consts.START_ARRAY
        elif ch == ']':
            self._pos+=1
            return consts.END_ARRAY
        elif ch == '"':
            m = _STRING(self._data, self._pos)
            self._pos = m.end()
            value = m.group()
            kw = _KEYWORDS.get(value)
            if not kw:
                self._value = value
            return kw or consts.STRING
        elif ch == 'n':
            if self._data[self._pos+1] == 'u' and self._data[self._pos+2] == 'l' and self._data[self._pos+3] == 'l':
                self._pos = self._pos+4
                return consts.KW_NULL
        return None

    def _eat(self):
        m = _IGNORE(self._data, self._pos)
        while m:
            self._pos = m.end()
            m = _IGNORE(self._data, self._pos)

if __name__ == '__main__':
    test_data = [
                 ' {"version": "1.0", "item_type": "topicmap"}',
                 ' {"version": "1.0", "item_type": "topicmap", "reifier": null}', 
                 ]
    for data in test_data:
        lexer = Lexer(data)
        while True:
            tok = lexer.token()
            if not tok: break
            print(tok)

