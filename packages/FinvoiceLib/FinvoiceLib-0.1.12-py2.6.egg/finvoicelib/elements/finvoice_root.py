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


from finvoicelib.elements import BuyerCommunicationDetails
from finvoicelib.elements import BuyerContactPersonName
from finvoicelib.elements import BuyerOrganisationUnitNumber
from finvoicelib.elements import BuyerOrganisationTaxCode
from finvoicelib.elements import BuyerPartyDetails
from finvoicelib.elements import DeliveryCommunicationDetails
from finvoicelib.elements import DeliveryContactPersonName
from finvoicelib.elements import DeliveryDetails
from finvoicelib.elements import DeliveryPartyDetails
from finvoicelib.elements import Element
from finvoicelib.elements import EpiDetails
from finvoicelib.elements import InvoiceDetails
from finvoicelib.elements import InvoiceRecipientPartyDetails
from finvoicelib.elements import InvoiceRow
from finvoicelib.elements import InvoiceSenderPartyDetails
from finvoicelib.elements import InvoiceUrlNameText
from finvoicelib.elements import InvoiceUrlText
from finvoicelib.elements import PaymentStatusDetails
from finvoicelib.elements import SellerCommunicationDetails
from finvoicelib.elements import SellerContactPersonName
from finvoicelib.elements import SellerInformationDetails
from finvoicelib.elements import SellerOrganisationUnitNumber
from finvoicelib.elements import SellerOrganisationTaxCode
from finvoicelib.elements import SellerPartyDetails
from finvoicelib.elements import SpecificationDetails
from finvoicelib.elements import VirtualBankBarcode


class FinvoiceRoot(Element):
    """
    FinvoiceRoot wrapper for the <Finvoice> element
    """
    tag = 'finvoice'
    aggregate = [
        BuyerCommunicationDetails,
        BuyerOrganisationUnitNumber,
        BuyerOrganisationTaxCode,
        BuyerContactPersonName,
        BuyerPartyDetails,
        DeliveryDetails,
        DeliveryPartyDetails,
        DeliveryContactPersonName,
        DeliveryCommunicationDetails,
        EpiDetails,
        InvoiceDetails,
        InvoiceRecipientPartyDetails,
        InvoiceRow,
        InvoiceSenderPartyDetails,
        InvoiceUrlNameText,
        InvoiceUrlText,
        PaymentStatusDetails,
        SellerCommunicationDetails,
        SellerContactPersonName,
        SellerInformationDetails,
        SellerPartyDetails,
        SellerOrganisationUnitNumber,
        SellerOrganisationTaxCode,
        SpecificationDetails,
        VirtualBankBarcode, ]

    def set_attributes(self):
        self.attributes = {'version': None}
