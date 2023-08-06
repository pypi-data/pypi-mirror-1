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


from finvoicelib.elements import DateElement
from finvoicelib.elements import Element
from finvoicelib.elements.country import CountryName


class ManufacturerCountryCode(Element):
    """
    ManufacturerCountryCode
    """
    tag = 'ManufacturerCountryCode'


class ManufacturerCountryName(Element):
    """
    ManufacturerCountryName
    """
    tag = 'ManufacturerCountryName'


class ManufacturerIdentifier(Element):
    """
    ManufacturerIdentifier
    """
    tag = 'ManufacturerIdentifier'


class ManufacturerName(Element):
    """
    ManufacturerName
    """
    tag = 'ManufacturerName'


class DelivererCountryCode(Element):
    """
    DelivererCountryCode
    """
    tag = 'DelivererCountryCode'


class DelivererCountryName(Element):
    """
    DelivererCountryName
    """
    tag = 'DelivererCountryName'


class DelivererIdentifier(Element):
    """
    DelivererIdentifier
    """
    tag = 'DelivererIdentifier'


class DelivererName(Element):
    """
    DelivererName
    """
    tag = 'DelivererName'


class DeliveryDate(DateElement):
    """
    DeliveryDate
    """
    tag = 'DeliveryDate'


class DeliveryMethodText(Element):
    """
    DeliveryMethodText
    """
    tag = 'DeliveryMethodText'


class DeliveryOrganisationName(Element):
    """
    DeliveryOrganisationName
    """
    tag = 'DeliveryOrganisationName'


class DeliveryPartyIdentifier(Element):
    """
    DeliveryPartyIdentifier
    """
    tag = 'DeliveryPartyIdentifier'


class DeliveryPostCodeIdentifier(Element):
    """
    DeliveryPostCodeIdentifier
    """
    tag = 'DeliveryPostCodeIdentifier'


class DeliveryPostofficeBoxIdentifier(Element):
    """
    DeliveryPostofficeBoxIdentifier
    """
    tag = 'DeliveryPostofficeBoxIdentifier'


class DeliveryStreetName(Element):
    """
    DeliveryStreetName
    """
    tag = 'DeliveryStreetName'


class DeliveryTermsText(Element):
    """
    DeliveryTermsText
    """
    tag = 'DeliveryTermsText'


class TerminalAddressText(Element):
    """
    TerminalAddressText
    """
    tag = 'TerminalAddressText'


class WaybillIdentifier(Element):
    """
    WaybillIdentifier
    """
    tag = 'WaybillIdentifier'


class WaybillTypeCode(Element):
    """
    WaybillTypeCode
    """
    tag = 'WaybillTypeCode'


class DeliveryTownName(Element):
    """
    DeliveryTownName
    """
    tag = 'DeliveryTownName'


class DeliveryEmailaddressIdentifier(Element):
    """
    DeliveryEmailaddressIdentifier
    """
    tag = 'DeliveryEmailaddressIdentifier'


class DeliveryPhoneNumberIdentifier(Element):
    """
    DeliveryPhoneNumberIdentifier
    """
    tag = 'DeliveryPhoneNumberIdentifier'


class DeliveryCommunicationDetails(Element):
    """
    DeliveryCommunicationDetails
    """
    tag = 'DeliveryCommunicationDetails'
    aggregate = [DeliveryEmailaddressIdentifier,
        DeliveryPhoneNumberIdentifier]


class DeliveryContactPersonName(Element):
    """
    DeliveryContactPersonName
    """
    tag = 'DeliveryContactPersonName'


class DeliveryContactPersonEmail(Element):
    """
    DeliveryContactPersonName
    """
    tag = 'DeliveryContactPersonEmail'


class DeliveryPostalAddressDetails(Element):
    """
    DeliveryPostalAddressDetails
    """
    tag = 'DeliveryPostalAddressDetails'
    aggregate = [DeliveryStreetName,
        DeliveryTownName,
        DeliveryPostCodeIdentifier,
        CountryName,
        DeliveryPostofficeBoxIdentifier]


class DeliveryPartyDetails(Element):
    """
    DeliveryPartyDetails
    """
    tag = 'DeliveryPartyDetails'
    aggregate = [DeliveryPartyIdentifier,
        DeliveryOrganisationName,
        DeliveryPostalAddressDetails]


class DeliveryDetails(Element):
    """
    DeliveryDetails
    """
    tag = 'DeliveryDetails'
    aggregate = [DeliveryDate,
        DeliveryMethodText,
        DeliveryTermsText,
        TerminalAddressText,
        WaybillIdentifier,
        WaybillTypeCode,
        DelivererIdentifier,
        DelivererName,
        DelivererName,
        DelivererCountryCode,
        DelivererCountryName,
        ManufacturerIdentifier,
        ManufacturerName,
        ManufacturerCountryCode,
        ManufacturerCountryName]
