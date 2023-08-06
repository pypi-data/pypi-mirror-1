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
from tm import mio, TMDM, XSD, irilib
from mio.reader.jtm._json import unescape
from mio.reader.jtm import consts

_TOPIC_NAME = mio.SUBJECT_IDENTIFIER, TMDM.topic_name

class JTMParser(object):
    """\
    JTM parser which accepts only 'nicely formatted' JSON Topic Maps.
    """
    def __init__(self, base, lexer, encoding=None):
        self._base = base
        self._lexer = lexer
        self._current = None
        self._encoding = encoding or 'utf-8'

    def _token(self):
        """\
        Moves the lexer to the next token and returns the token *type*.
        The current token (incl. its value) is kept in ``self._current``.
        """
        self._current = self._lexer.token()
        return self._current
    
    def _value(self):
        """\
        Returns the unescaped value of the current token.
        """
        return unescape(self._lexer.value(), encoding=self._encoding)

    def _resolve_iri(self, ref):
        return irilib.resolve_iri(self._base, ref) 

    def parse(self, handler):
        """\
        
        `handler`
            A MapHandler instance.
        """
        token = self._token
        if token() != consts.START_OBJECT:
            raise mio.MIOException('Expected data to start with an object ("{")')
        if token() != consts.KW_VERSION:
            raise mio.MIOException('Expected a version information at the top')
        token()
        if '1.0' != self._value():
            raise mio.MIOException('Unsupported version: "%s"' % self._value())
        if token() != consts.KW_ITEM_TYPE:
            raise mio.MIOException('Expected "item_type" after the version')
        if self._handle_itemtype(handler):
            return
        while token() != consts.END_OBJECT:
            tok = self._current
            if tok == consts.KW_IIDS:
                self._handle_iids(handler)
            elif tok == consts.KW_REIFIER:
                self._handle_reifier(handler)
            elif tok == consts.KW_TOPICS:
                handle_topic = self._handle_topic
                if token() == consts.START_ARRAY:
                    while token() != consts.END_ARRAY:
                        handle_topic(handler)
                else:
                    raise mio.MIOException('Expected an array of topics')
            elif tok == consts.KW_ASSOCIATIONS:
                handle_association = self._handle_association
                if token() == consts.START_ARRAY:
                    while token() != consts.END_ARRAY:
                        handle_association(handler)
                else:
                    raise mio.MIOException('Expected an array of associations')
            else:
                self._report_illegalfield()

    def _handle_itemtype(self, handler):
        """\
        Reads the item type and returns if the Topic Maps construct has been 
        parsed completely.
        """
        self._token()
        itemtype = self._value().lower()
        if itemtype == 'topicmap':
            return False
        if itemtype == 'topic':
            self._handle_topic(handler)
        elif itemtype == 'association':
            self._handle_association(handler)
        elif itemtype == 'occurrence':
            self._handle_parent_topic(handler)
            self._handle_occurrence(handler)
            handler.endTopic()
        elif itemtype == 'name':
            self._handle_parent_topic(handler)
            self._handle_name(handler)
            handler.endTopic()
        else:
            if itemtype not in ('role', 'variant'):
                raise mio.MIOException('Unknown item_type: "%s"' % itemtype)
            else:
                raise mio.MIOException('Detached variants and roles are not supported')
        return True

    def _topic_ref(self):
        prefix, ref = self._value().split(':', 1)
        iri = self._resolve_iri(ref)
        if prefix == 'ii':
            return mio.ITEM_IDENTIFIER, iri
        elif prefix == 'si':
            return mio.SUBJECT_IDENTIFIER, iri
        elif prefix == 'sl':
            return mio.SUBJECT_LOCATOR, iri
        raise mio.MIOException('Unknown topic reference: "%s"' % ref)

    def _handle_parent_topic(self, handler):
        token, topic_ref = self._token, self._topic_ref
        if token() != consts.KW_PARENT:
            raise mio.MIOException('Expected a "parent" field')
        if token() != consts.START_ARRAY:
            raise mio.MIOException('Expected an array for the parent value')
        token()
        handler.startTopic(topic_ref())
        while token() != consts.END_ARRAY:
            kind, iri = topic_ref()
            if kind == mio.ITEM_IDENTIFIER:
                handler.itemIdentifier(iri)
            elif kind == mio.SUBJECT_IDENTIFIER:
                handler.subjectIdentifier(iri)
            elif kind == mio.SUBJECT_LOCATOR:
                handler.subjectLocator(iri)
            else:
                raise mio.MIOException('Unknown reference type: %s' % kind)

    def _handle_topic(self, handler):
        def read_identities(kind, identity_fn):
            topic_started = seen_identity
            if token() == consts.START_ARRAY:
                while token() != consts.END_ARRAY:
                    iri = resolve_iri(value())
                    if not topic_started:
                        handler.startTopic((kind, iri))
                        topic_started = True
                    else:
                        identity_fn(iri)
            return topic_started
        if self._current != consts.START_OBJECT:
            raise mio.MIOException("Expected a topic start" + self._current)
        seen_identity = False
        token, value, resolve_iri = self._token, self._value, self._resolve_iri
        while token() != consts.END_OBJECT:
            tok = self._current
            if tok == consts.KW_SIDS:
                seen_identity = read_identities(mio.SUBJECT_IDENTIFIER, handler.subjectIdentifier)
            elif tok == consts.KW_SLOS:
                seen_identity = read_identities(mio.SUBJECT_LOCATOR, handler.subjectLocator)
            elif tok == consts.KW_IIDS:
                seen_identity = read_identities(mio.ITEM_IDENTIFIER, handler.itemIdentifier)
            elif tok == consts.KW_OCCURRENCES:
                if token() == consts.START_ARRAY:
                    if not seen_identity:
                        raise mio.MIOException('Cannot process occurrences without a previously read identity')
                    handle_occurrence = self._handle_occurrence
                    while token() != consts.END_ARRAY:
                        handle_occurrence(handler)
            elif tok == consts.KW_NAMES:
                if token() == consts.START_ARRAY:
                    if not seen_identity:
                        raise mio.MIOException('Cannot process names without a previously read identity')
                    handle_name = self._handle_name
                    while token() != consts.END_ARRAY:
                        handle_name(handler)
            else:
                self._report_illegalfield()
        if not seen_identity:
            raise mio.MIOException('The topic has no identity')
        handler.endTopic()

    def _handle_occurrence(self, handler):
        seen_type = False
        token = self._token
        value, datatype = None, XSD.string
        handler.startOccurrence()
        while token() != consts.END_OBJECT:
            tok = self._current
            if tok == consts.KW_TYPE:
                if not seen_type:
                    token()
                    handler.type(self._topic_ref())
                    seen_type = True
            elif tok == consts.KW_VALUE:
                token()
                value = self._value()
            elif tok == consts.KW_DATATYPE:
                token()
                datatype = self._value()
            elif tok == consts.KW_IIDS:
                self._handle_iids(handler)
            elif tok == consts.KW_REIFIER:
                self._handle_reifier(handler)
            elif tok == consts.KW_SCOPE:
                self._handle_scope(handler)
            else:
                self._report_illegalfield()
        if value is None:
            raise mio.MIOException('The value of the occurrence is undefined')
        handler.value(value, datatype)
        if not seen_type:
            raise mio.MIOException('The type of the occurrence is undefined')
        handler.endOccurrence()

    def _handle_name(self, handler):
        seen_type = False
        token = self._token
        value = None
        handler.startName()
        while token() != consts.END_OBJECT:
            tok = self._current
            if tok == consts.KW_TYPE:
                if not seen_type:
                    token()
                    handler.type(self._topic_ref())
                    seen_type = True
            elif tok == consts.KW_VALUE:
                token()
                value = self._value()
            elif tok == consts.KW_IIDS:
                self._handle_iids(handler)
            elif tok == consts.KW_REIFIER:
                self._handle_reifier(handler)
            elif tok == consts.KW_SCOPE:
                self._handle_scope(handler)
            elif tok == consts.KW_VARIANTS:
                if token() == consts.START_ARRAY:
                    handle_variant = self._handle_variant
                    while token() != consts.END_ARRAY:
                        handle_variant(handler)
            else:
                self._report_illegalfield()
        if value is None:
            raise mio.MIOException('The value of the name is undefined')
        handler.value(value)
        if not seen_type:
            handler.type(_TOPIC_NAME)
        handler.endName()

    def _handle_variant(self, handler):
        token = self._token
        value, datatype = None, XSD.string
        seen_scope = False
        handler.startVariant()
        while token() != consts.END_OBJECT:
            tok = self._current
            if tok == consts.KW_VALUE:
                token()
                value = self._value()
            elif tok == consts.KW_DATATYPE:
                token()
                datatype = self._value()
            elif tok == consts.KW_IIDS:
                self._handle_iids(handler)
            elif tok == consts.KW_REIFIER:
                self._handle_reifier(handler)
            elif tok == consts.KW_SCOPE:
                if not seen_scope:
                    self._handle_scope(handler)
                    seen_scope = True
            else:
                self._report_illegalfield()
        if not seen_scope:
            raise mio.MIOException('The scope of the variant is undefined')
        if value is None:
            raise mio.MIOException('The value of the variant is undefined')
        handler.value(value, datatype)
        handler.endVariant()

    def _handle_association(self, handler):
        """\
        
        """
        seen_type, seen_roles = False, False
        token, handle_role = self._token, self._handle_role
        handler.startAssociation()
        while token() != consts.END_OBJECT:
            tok = self._current
            if tok == consts.KW_TYPE:
                if not seen_type:
                    token()
                    handler.type(self._topic_ref())
                    seen_type = True
                else:
                    raise mio.MIOException('The type of the association is defined twice')
            elif tok == consts.KW_IIDS:
                self._handle_iids(handler)
            elif tok == consts.KW_REIFIER:
                self._handle_reifier(handler)
            elif tok == consts.KW_SCOPE:
                self._handle_scope(handler)
            elif tok == consts.KW_ROLES:
                if not seen_roles and token() == consts.START_ARRAY:
                    while token() != consts.END_ARRAY:
                        handle_role(handler)
                    seen_roles = True
                else:
                    raise mio.MIOException('Invalid "roles" definition')
            else:
                self._report_illegalfield()
        if not seen_type:
            raise mio.MIOException('The type of the association is undefined')
        if not seen_roles:
            raise mio.MIOException('The association has no roles')
        handler.endAssociation()

    def _handle_role(self, handler):
        
        seen_type, seen_player = False, False
        token = self._token
        handler.startRole()
        while token() != consts.END_OBJECT:
            tok = self._current
            if tok == consts.KW_TYPE:
                if not seen_type:
                    token()
                    handler.type(self._topic_ref())
                    seen_type = True
                else:
                    raise mio.MIOException('The type of the role is defined twice')
            elif tok == consts.KW_PLAYER:
                if not seen_player:
                    token()
                    handler.player(self._topic_ref())
                    seen_player = True
                else:
                    raise mio.MIOException('The player of the role is defined twice')
            elif tok == consts.KW_IIDS:
                self._handle_iids(handler)
            elif tok == consts.KW_REIFIER:
                self._handle_reifier(handler)
            else:
                self._report_illegalfield()
        if not seen_type:
            raise mio.MIOException('The type of the role is undefined')
        if not seen_player:
            raise mio.MIOException('The player of the role is undefined')
        handler.endRole()

    def _handle_iids(self, handler):
        token, value, resolve_iri = self._token, self._value, self._resolve_iri
        if token() != consts.START_ARRAY:
            raise mio.MIOException('Expected an array for the item identifiers')
        while token() != consts.END_ARRAY:
            handler.itemIdentifier(resolve_iri(value()))

    def _handle_scope(self, handler):
        token, topic_ref = self._token, self._topic_ref
        if token() != consts.START_ARRAY:
            raise mio.MIOException('Expected an array for the scope themes')
        handler.startScope()
        while token() != consts.END_ARRAY:
            handler.theme(topic_ref())
        handler.endScope()

    def _handle_reifier(self, handler):
        if self._token() != consts.KW_NULL:
            handler.reifier(self._topic_ref())

    def _report_illegalfield(self):
        raise mio.MIOException('Unknown field name: %s' % self._value())
