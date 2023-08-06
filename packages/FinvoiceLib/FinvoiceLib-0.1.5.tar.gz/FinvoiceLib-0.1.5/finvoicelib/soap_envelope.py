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


class SoapEnvelope(object):

    seller_id = None
    seller_intermediator_id = None
    buyer_id = None
    buyer_intermediator_id = None

    def __init__(self, tree):

        ns = tree.nsmap.get('eb')

        def build_xpath(elem, role):
            return ('//{%(N)s}%(elem)s/{%(N)s}'
                    'PartyId[../{%(N)s}Role'
                    ' = "%(role)s"]/text()'
                    % {'N': ns, 'elem': elem, 'role': role})

        # Functions for finding net service ids
        get_seller_id = etree.ETXPath(build_xpath('From', 'Sender'))
        get_seller_intermed_id = \
            etree.ETXPath(build_xpath('From', 'Intermediator'))

        get_buyer_id = etree.ETXPath(build_xpath('To', 'Receiver'))
        get_buyer_intermed_id = \
            etree.ETXPath(build_xpath('To', 'Intermediator'))

        seller_id = get_seller_id(tree)
        if len(seller_id)>0:
            self.seller_id = str(seller_id[0])

        seller_intermediator_id = get_seller_intermed_id(tree)
        if len(seller_intermediator_id)>0:
            self.seller_intermediator_id = seller_intermediator_id[0]

        buyer_id = get_buyer_id(tree)
        if len(buyer_id)>0:
            self.buyer_id = str(buyer_id[0])

        buyer_intermediator_id = get_buyer_intermed_id(tree)
        if len(buyer_intermediator_id)>0:
            self.buyer_intermediator_id = buyer_intermediator_id[0]
