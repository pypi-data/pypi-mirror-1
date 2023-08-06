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


class Block(object):

    block_type = None
    start = None
    end = None
    env_data = None
    data = None

    def __init__(self, block_type):
        self.block_type = block_type
        self.start = None
        self.end = None
        self.soap = ''
        self.payload = ''


class FinvoiceXmlReader(object):

    filename = None

    def __init__(self, file_object):
        self.file_object = file_object

    def __iter__(self):
        soap_env_open = False
        finvoice_open = False
        msg = None
        blocks = []
        for line in self.file_object:
            if not line.strip().startswith('<?xml'):
                if line.strip().startswith('<SOAP-ENV:Envelope'):
                    if finvoice_open:
                        blocks.append(msg)
                        finvoice_open = False
                        yield msg
                    soap_env_open = True
                    msg = Block('SOAP-ENV')
                elif line.strip().startswith('</SOAP-ENV:Envelope>'):

                    soap_env_open = False
                    finvoice_open = True
                    msg.soap += line
                    continue
            else:
                if not finvoice_open:
                    finvoice_open = True
                    msg = Block('SOAP-ENV')

            if soap_env_open:
                msg.soap += line
            elif finvoice_open:
                msg.payload += line
        yield msg
