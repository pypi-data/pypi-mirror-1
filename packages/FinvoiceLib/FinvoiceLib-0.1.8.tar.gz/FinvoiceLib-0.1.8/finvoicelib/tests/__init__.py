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


import random
from pkg_resources import resource_stream
from unittest import TestCase


class FinvoiceTestCase(TestCase):

    def __init__(self, * args, ** kwargs):
        super(FinvoiceTestCase, self).__init__(*args, ** kwargs)

    def get_pulli_finvoice(self):
        """
        get_pulli_finvoice

        Return a file-object of the Pulli Finvoice example file.

        URL:
        http://www.pankkiyhdistys.fi/verkkolasku/yrityksen_verkkolasku/
        ladattavat/Tekniset%20tiedostot/mallit/yrityksen%20vl/
        Pulli_laaja_20041215.xml

        """
        return resource_stream(__name__,
                               '../resources/Pulli_laaja_20041215.xml')

    def get_pankkiyhdistys_finvoice(self):
        """
        get_pankkiyhdistys_finvoice

        Return to a file-object to the file
        "Finvoice_peruslasku_kehystetty.xml"

        This file has a additional SOAP-envelope.
        And this file is actually invalid xml. So there, go have fun!

        """
        return resource_stream(__name__,
                               '../resources' \
                               '/Finvoice_peruslasku_kehystetty.xml')
