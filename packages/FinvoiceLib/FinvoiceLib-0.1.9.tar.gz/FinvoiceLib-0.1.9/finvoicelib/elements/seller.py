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


from finvoicelib.elements import BusinessIdElement
from finvoicelib.elements import Element
from finvoicelib.elements.country import CountryCode
from finvoicelib.elements.country import CountryName


class SellerOrganisationUnitNumber(Element):
    """
    SellerOrganisationUnitNumber
    """
    tag = 'SellerOrganisationUnitNumber'


class SellerPhoneNumberIdentifier(Element):
    """
    SellerPhoneNumberIdentifier
    """
    tag = 'SellerPhoneNumberIdentifier'


class SellerVatRegistrationDate(Element):
    """
    SellerVatRegistrationDate
    """
    tag = 'SellerVatRegistrationDate'


class SellerVatRegistrationText(Element):
    """
    SellerVatRegistrationText
    """
    tag = 'SellerVatRegistrationText'


class SellerAccountID(Element):
    """
    SellerAccountID
    """
    tag = 'SellerAccountID'


class SellerBic(Element):
    """
    SellerBic
    """
    tag = 'SellerBic'


class SellerAccountDetails(Element):
    """
    SellerAccountDetails
    """
    tag = 'SellerAccountDetails'
    aggregate = [SellerAccountID, SellerBic]


class SellerCommonEmailaddressIdentifier(Element):
    """
    SellerCommonEmailaddressIdentifier
    """
    tag = 'SellerCommonEmailaddressIdentifier'


class SellerContactPersonName(Element):
    """
    SellerContactPersonName
    """
    tag = 'SellerContactPersonName'


class SellerEmailaddressIdentifier(Element):
    """
    SellerEmailaddressIdentifier
    """
    tag = 'SellerEmailaddressIdentifier'


class SellerCommunicationDetails(Element):
    """
    SellerCommunicationDetails
    """
    tag = 'SellerCommunicationDetails'
    aggregate = [SellerEmailaddressIdentifier,
        SellerPhoneNumberIdentifier]


class SellerFaxNumber(Element):
    """
    SellerFaxNumber
    """
    tag = 'SellerFaxNumber'


class SellerFreeText(Element):
    """
    SellerFreeText
    """
    tag = 'SellerFreeText'


class SellerHomeTownName(Element):
    """
    SellerHomeTownName
    """
    tag = 'SellerHomeTownName'


class SellerOrganisationName(Element):
    """
    SellerOrganisationName
    """
    tag = 'SellerOrganisationName'


class SellerOrganisationTaxCode(Element):
    """
    SellerOrganisationTaxCode
    """
    tag = 'SellerOrganisationTaxCode'

class SellerOrganisationTaxCodeUrlText(Element):
    """
    SellerOrganisationTaxCodeUrlText
    """
    tag = 'SellerOrganisationTaxCodeUrlText'


class SellerPartyIdentifier(BusinessIdElement):
    """
    SellerPartyIdentifier
    """
    tag = 'SellerPartyIdentifier'


class SellerPhoneNumber(Element):
    """
    SellerPhoneNumber
    """
    tag = 'SellerPhoneNumber'


class SellerPostCodeIdentifier(Element):
    """
    SellerPostCodeIdentifier
    """
    tag = 'SellerPostCodeIdentifier'


class SellerReferenceIdentifier(Element):
    """
    SellerReferenceIdentifier
    """
    tag = 'SellerReferenceIdentifier'


class SellerStreetName(Element):
    """
    SellerStreetName
    """
    tag = 'SellerStreetName'


class SellerTownName(Element):
    """
    SellerTownName
    """
    tag = 'SellerTownName'


class SellerWebaddressIdentifier(Element):
    """
    SellerWebaddressIdentifier
    """
    tag = 'SellerWebaddressIdentifier'


class SellerPostalAddressDetails(Element):
    """
    SellerPostalAddressDetails
    """
    tag = 'SellerPostalAddressDetails'
    aggregate = [SellerStreetName,
        SellerTownName,
        SellerPostCodeIdentifier,
        CountryCode,
        CountryName]


class SellerPartyDetails(Element):
    """
    SellerPartyDetails
    """
    tag = 'SellerPartyDetails'
    aggregate = [SellerPartyIdentifier,
        SellerOrganisationName,
        SellerOrganisationTaxCode,
        SellerOrganisationTaxCodeUrlText,
        SellerPostalAddressDetails]


class InvoiceRecipientOrganisationName(Element):
    """
    InvoiceRecipientOrganisationName
    """
    tag = 'InvoiceRecipientOrganisationName'


class InvoiceRecipientPartyIdentifier(Element):
    """
    InvoiceRecipientPartyIdentifier
    """
    tag = 'InvoiceRecipientPartyIdentifier'


class InvoiceRecipientOrganisationTaxCode(Element):
    """
    InvoiceRecipientOrganisationName
    """
    tag = 'InvoiceRecipientOrganisationTaxCode'


class InvoiceRecipientPostCodeIdentifier(Element):
    """
    InvoiceRecipientPostCodeIdentifier
    """
    tag = 'InvoiceRecipientPostCodeIdentifier'


class InvoiceRecipientPostOfficeBoxIdentifier(Element):
    """
    InvoiceRecipientPostOfficeBoxIdentifier
    """
    tag = 'InvoiceRecipientPostOfficeBoxIdentifier'


class InvoiceRecipientStreetName(Element):
    """
    InvoiceRecipientStreetName
    """
    tag = 'InvoiceRecipientStreetName'


class InvoiceRecipientTownName(Element):
    """
    InvoiceRecipientTownName
    """
    tag = 'InvoiceRecipientTownName'


class InvoiceRecipientAddress(Element):
    """
    InvoiceRecipientAddress
    """
    tag = 'InvoiceRecipientAddress'


class InvoiceRecipientIntermediatorAddress(Element):
    """
    InvoiceRecipientIntermediatorAddress
    """
    tag = 'InvoiceRecipientIntermediatorAddress'


class InvoiceRecipientDetails(Element):
    """
    InvoiceRecipientDetails
    """
    tag = 'InvoiceRecipientDetails'
    aggregate = [InvoiceRecipientAddress,
        InvoiceRecipientIntermediatorAddress]


class SellerInformationDetails(Element):
    """
    SellerInformationDetails
    """
    tag = 'SellerInformationDetails'
    aggregate = [SellerHomeTownName,
        SellerPhoneNumber,
        SellerFaxNumber,
        SellerCommonEmailaddressIdentifier,
        SellerWebaddressIdentifier,
        SellerFreeText,
        SellerAccountDetails,
        SellerAccountDetails,
        SellerAccountDetails,
        InvoiceRecipientDetails,
        SellerVatRegistrationText,
        SellerVatRegistrationDate]


class InvoiceRecipientPostalAddressDetails(Element):
    """
    InvoiceRecipientPostalAddressDetails
    """
    tag = 'InvoiceRecipientPostalAddressDetails'
    aggregate = [InvoiceRecipientStreetName,
        InvoiceRecipientTownName,
        InvoiceRecipientPostCodeIdentifier,
        CountryCode,
        CountryName,
        InvoiceRecipientPostOfficeBoxIdentifier]


class InvoiceRecipientPartyDetails(Element):
    """
    InvoiceRecipientPartyDetails
    """
    tag = 'InvoiceRecipientPartyDetails'
    aggregate = [InvoiceRecipientPartyIdentifier,
        InvoiceRecipientOrganisationName,
        InvoiceRecipientOrganisationTaxCode,
            InvoiceRecipientPostalAddressDetails, ]
