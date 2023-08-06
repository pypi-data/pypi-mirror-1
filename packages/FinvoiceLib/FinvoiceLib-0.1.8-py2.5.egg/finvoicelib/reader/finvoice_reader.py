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


from lxml import etree
from lxml import objectify
from pkg_resources import resource_stream

from finvoicelib.error import LxmlErrorWrapper
from finvoicelib.reader.message import Message
from finvoicelib.reader.xml_reader import FinvoiceXmlReader


class Reader(object):
    """

    Finvoice file may contain more than one message.

    Message consists of:
     * SOAP-Envelop (ebxml) (optional)
     * Finvoice-xml

    """

    errors = None
    messages = None
    dtd_resource = '../resources/Finvoice.dtd'

    def __init__(self, xml):
        if isinstance(xml, basestring):
            f = open(xml)
        else:
            f = xml

        self.errors = []
        self.messages = []

        r = FinvoiceXmlReader(f)

        for block in r:
            # SOAP-ENVELOPE
            if block.soap:
                env = etree.XML(block.soap)
            else:
                env = None
            # Payload
            xml_tree = objectify.XML(block.payload)
            msg = Message(xml_tree, env)
            if not self.validate(xml_tree):
                print 'Invalid XML!'
                msg.errors += self.errors
            self.messages.append(msg)

    def validate(self, xml_tree):
        f = resource_stream(__name__, self.dtd_resource)
        dtd = etree.DTD(f)
        if dtd.validate(xml_tree):
            return True
        for error in dtd.error_log.filter_from_errors():
            self.errors.append(LxmlErrorWrapper(error))
        return False
