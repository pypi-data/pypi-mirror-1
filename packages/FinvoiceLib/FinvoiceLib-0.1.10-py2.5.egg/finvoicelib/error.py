#!/usr/bin/python
# coding: utf-8
#
# Copyright (c) 2009, Norfello Oy
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the Norfello Oy nor the
#      names of its contributors may be used to endorse or promote products
#      derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY NORFELLO OY ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL NORFELLO OY BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


class ElementError(object):

    error_type = 'ERROR'
    tag = ''
    msg_id = ''
    description = ''
    line = None
    msg_origin = ''

    def __init__(self, node, description=None):
        self.tag = node.tag
        self.line = node.sourceline
        if description:
            self.description = description

    def get_message(self):
        fmt = ('<unknown>:%(sourceline)s:%(type)s:%(msg_origin)s:%(element)s:'
               '%(message)s:' \
                   ' %(description)s')
        return fmt % {'type': self.error_type,
            'sourceline': self.line,
            'element': self.tag,
            'message': self.msg_id,
            'description': self.description}


class Warning(ElementError):
    error_type = 'WARNING'


class VersionWarning(Warning):
    msg_id = 'INCOMPATIBLE_FINVOICE_VERSION'

    def __init__(self, description):
        self.description = description


class ElementMissingError(ElementError):
    error_type = 'ERROR'
    msg_id = 'ELEMENT_MISSING'

    def __init__(self, node, msg_extra=''):
        self.line = node.sourceline
        self.node = node
        self.description = msg_extra


class UnknownAttributeWarning(Warning):
    msg_id = "UNKNOWN_ATTRIBUTE"


class UnknownElementWarning(Warning):
    msg_id = "UNKNOWN_ELEMENT"


class InvalidValue(ElementError):
    msg_id = 'INVALID_VALUE'


class LxmlErrorWrapper(ElementError):

    def __init__(self, msg):
        msg_parts = str(msg).split(':')
        self.line = msg_parts[1]
        self.msg_id = 'DTD_VALIDATION'
        self.description = msg_parts[-1]

    def get_message(self):
        return self.description


class ValueMismatchError(ElementError):
    error_type = 'ERROR'
    msg_id = 'VALUE_MISMATCH'
    line = -1
    node = ''

    def __init__(self, description=''):
        self.description = description
