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


from StringIO import StringIO

from finvoicelib.reader.finvoice_reader import Reader
from finvoicelib.tests import FinvoiceTestCase


class TestReader(FinvoiceTestCase):

    document = None

    def test_init_with_pulli(self):
        """
        Test finvoice.reader.Reader.__init__ with "Pulli" finvoice
        """
        reader = Reader(self.get_pulli_finvoice())

        # Pulli finvoice has only one
        self.failUnless(len(reader.messages) == 1)

    def test_init_with_pankkiyhdistys_finvoice(self):
        """
        Test finvoice.reader.Reader.__init__ with "pankkiyhdistys" finvoice
        """
        reader = Reader(self.get_pankkiyhdistys_finvoice())

        # Pulli finvoice has only one
        self.failUnless(len(reader.messages) == 1)

    def test_init_with_combined_finvoice(self):
        """
        Test finvoice.reader.Reader.__init__ a combined finvoice

        """
        pulli_data = self.get_pulli_finvoice().read()
        pankkiyhdistys_data = self.get_pankkiyhdistys_finvoice().read()
        data = pulli_data + '\n' + pankkiyhdistys_data
        f = StringIO(data)
        reader = Reader(f)
        self.failUnless(len(reader.messages) == 2)
        self.assertEqual(reader.messages[0].envelope_tree, None)
        self.assertNotEqual(reader.messages[1].envelope_tree, None)
