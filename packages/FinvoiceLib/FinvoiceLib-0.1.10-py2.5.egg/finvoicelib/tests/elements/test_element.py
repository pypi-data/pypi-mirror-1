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


from finvoicelib.elements import Element
from finvoicelib.tests import FinvoiceTestCase


class TestElement(FinvoiceTestCase):

    def test_init_with_none(self):
        """
        Test finvoice.elements.Element.__init__ with tag=None
        """
        e = Element(None)
        self.assertEqual(e.tag, None)

    def test_init_with_tag(self):
        """
        Test finvoice.elements.Element.__init__ with tag='SomeElement'
        """
        e = Element('SomeElement')
        self.assertEqual(e.tag, 'SomeElement')


class TestElementSubclassing(FinvoiceTestCase):

    def setUp(self):

        class ChildElement(Element):
            tag = 'ChildElement'

        class SomeElement(Element):
            tag = 'SomeElement'
            aggregate = [ChildElement, ]

            def set_attributes(self):
                self.attributes = {'my_attr': None}

        self.some_element = SomeElement()

    def test_supported_elements(self):
        s = self.some_element
        self.assertEqual(s.supported_elements, ['ChildElement', ])

    def test_attributes(self):
        s = self.some_element
        self.assertEqual(s.my_attr, None)

    def test_has_mapping_for(self):
        s = self.some_element
        self.failUnless(s.has_mapping_for('ChildElement'))
        self.failIf(s.has_mapping_for('UnknownElement'))
