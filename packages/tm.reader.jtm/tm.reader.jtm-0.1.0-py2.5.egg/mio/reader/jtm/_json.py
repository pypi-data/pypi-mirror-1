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
JSON Topic Maps (JTM) 1.0 utilities.

:author:       Lars Heuer (heuer[at]semagia.com)
:organization: Semagia - http://www.semagia.com/
:version:      $Rev: 169 $ - $Date: 2009-06-26 14:44:17 +0200 (Fr, 26 Jun 2009) $
:license:      BSD license
"""
# Try to import some (json|simplejson) specific stuff. 
# If json or simplejson is available the string unescaping may operate faster 
# (at least if the C version of the decoder is available)
#pylint: disable-msg=E0102
found = False
try:
    #pylint: disable-msg=E0611, F0401
    from simplejson.decoder import scanstring
    found = True
except ImportError:
    pass
if not found:
    try:
        #pylint: disable-msg=F0401
        from json.encoder import scanstring
        found = True
    except ImportError:
        pass
if not found:
    # Code from simplejson.encoder Copyright (c) Bob Ippolito
    # License: MIT
    # http://undefined.org/python/#simplejson
    import re, sys
    FLAGS = re.VERBOSE | re.MULTILINE | re.DOTALL
    STRINGCHUNK = re.compile(r'(.*?)(["\\\x00-\x1f])', FLAGS)
    BACKSLASH = {
        '"': u'"', '\\': u'\\', '/': u'/',
        'b': u'\b', 'f': u'\f', 'n': u'\n', 'r': u'\r', 't': u'\t',
    }
    
    DEFAULT_ENCODING = "utf-8"
    def linecol(doc, pos):
        lineno = doc.count('\n', 0, pos) + 1
        if lineno == 1:
            colno = pos
        else:
            colno = pos - doc.rindex('\n', 0, pos)
        return lineno, colno
    
    def errmsg(msg, doc, pos, end=None):
        # Note that this function is called from _speedups
        lineno, colno = linecol(doc, pos)
        if end is None:
            #fmt = '{0}: line {1} column {2} (char {3})'
            #return fmt.format(msg, lineno, colno, pos)
            fmt = '%s: line %d column %d (char %d)'
            return fmt % (msg, lineno, colno, pos)
        endlineno, endcolno = linecol(doc, end)
        #fmt = '{0}: line {1} column {2} - line {3} column {4} (char {5} - {6})'
        #return fmt.format(msg, lineno, colno, endlineno, endcolno, pos, end)
        fmt = '%s: line %d column %d - line %d column %d (char %d - %d)'
        return fmt % (msg, lineno, colno, endlineno, endcolno, pos, end)    
    
    def py_scanstring(s, end, encoding=None, strict=True, _b=BACKSLASH, _m=STRINGCHUNK.match):
        """Scan the string s for a JSON string. End is the index of the
        character in s after the quote that started the JSON string.
        Unescapes all valid JSON string escape sequences and raises ValueError
        on attempt to decode an invalid string. If strict is False then literal
        control characters are allowed in the string.
        
        Returns a tuple of the decoded string and the index of the character in s
        after the end quote."""
        if encoding is None:
            encoding = DEFAULT_ENCODING
        chunks = []
        _append = chunks.append
        begin = end - 1
        while 1:
            chunk = _m(s, end)
            if chunk is None:
                raise ValueError(
                    errmsg("Unterminated string starting at", s, begin))
            end = chunk.end()
            content, terminator = chunk.groups()
            # Content is contains zero or more unescaped string characters
            if content:
                if not isinstance(content, unicode):
                    content = unicode(content, encoding)
                _append(content)
            # Terminator is the end of string, a literal control character,
            # or a backslash denoting that an escape sequence follows
            if terminator == '"':
                break
            elif terminator != '\\':
                if strict:
                    msg = "Invalid control character %r at" % (terminator,)
                    #msg = "Invalid control character {0!r} at".format(terminator)
                    raise ValueError(errmsg(msg, s, end))
                else:
                    _append(terminator)
                    continue
            try:
                esc = s[end]
            except IndexError:
                raise ValueError(
                    errmsg("Unterminated string starting at", s, begin))
            # If not a unicode escape sequence, must be in the lookup table
            if esc != 'u':
                try:
                    char = _b[esc]
                except KeyError:
                    msg = "Invalid \\escape: " + repr(esc)
                    raise ValueError(errmsg(msg, s, end))
                end += 1
            else:
                # Unicode escape sequence
                esc = s[end + 1:end + 5]
                next_end = end + 5
                if len(esc) != 4:
                    msg = "Invalid \\uXXXX escape"
                    raise ValueError(errmsg(msg, s, end))
                uni = int(esc, 16)
                # Check for surrogate pair on UCS-4 systems
                if 0xd800 <= uni <= 0xdbff and sys.maxunicode > 65535:
                    msg = "Invalid \\uXXXX\\uXXXX surrogate pair"
                    if not s[end + 5:end + 7] == '\\u':
                        raise ValueError(errmsg(msg, s, end))
                    esc2 = s[end + 7:end + 11]
                    if len(esc2) != 4:
                        raise ValueError(errmsg(msg, s, end))
                    uni2 = int(esc2, 16)
                    uni = 0x10000 + (((uni - 0xd800) << 10) | (uni2 - 0xdc00))
                    next_end += 6
                char = unichr(uni)
                end = next_end
            # Append the unescaped character
            _append(char)
        return u''.join(chunks), end
    
    scanstring = py_scanstring


from tm.mio import MIOException

def unescape(val, encoding='utf-8'):
    """\
    Unescapes the string.
    
    >>> unescape('"Semagia"')
    'Semagia'
    >>> unescape('"\u0022Semagia\u0022"')
    '"Semagia"'
    """
    try:
        return scanstring(val, 1, encoding)[0]
    except ValueError, ex:
        raise MIOException(ex)


if __name__ == '__main__':
    import doctest
    doctest.testmod()

