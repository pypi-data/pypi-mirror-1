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


from finvoice.elements import Element


class SubOriginalInvoiceNumber(Element):
    """
    SubOriginalInvoiceNumber
    """
    tag = 'SubOriginalInvoiceNumber'


class SubRowAccountDimensionText(Element):
    """
    SubRowAccountDimensionText
    """
    tag = 'SubRowAccountDimensionText'


class SubRowAgreementIdentifier(Element):
    """
    SubRowAgreementIdentifier
    """
    tag = 'SubRowAgreementIdentifier'


class SubRowAmount(Element):
    """
    SubRowAmount
    """
    tag = 'SubRowAmount'


class SubRowDelivererCountryCode(Element):
    """
    SubRowDelivererCountryCode
    """
    tag = 'SubRowDelivererCountryCode'


class SubRowDelivererCountryName(Element):
    """
    SubRowDelivererCountryName
    """
    tag = 'SubRowDelivererCountryName'


class SubRowDelivererIdentifier(Element):
    """
    SubRowDelivererIdentifier
    """
    tag = 'SubRowDelivererIdentifier'


class SubRowDelivererName(Element):
    """
    SubRowDelivererName
    """
    tag = 'SubRowDelivererName'


class SubRowDeliveryDate(Element):
    """
    SubRowDeliveryDate
    """
    tag = 'SubRowDeliveryDate'


class SubRowDeliveryIdentifier(Element):
    """
    SubRowDeliveryIdentifier
    """
    tag = 'SubRowDeliveryIdentifier'


class SubRowIdentifier(Element):
    """
    SubRowIdentifier
    """
    tag = 'SubRowIdentifier'


class SubRowIdentifierDate(Element):
    """
    SubRowIdentifierDate
    """
    tag = 'SubRowIdentifierDate'


class SubRowManufacturerCountryCode(Element):
    """
    SubRowManufacturerCountryCode
    """
    tag = 'SubRowManufacturerCountryCode'


class SubRowManufacturerCountryName(Element):
    """
    SubRowManufacturerCountryName
    """
    tag = 'SubRowManufacturerCountryName'


class SubRowManufacturerIdentifier(Element):
    """
    SubRowManufacturerIdentifier
    """
    tag = 'SubRowManufacturerIdentifier'


class SubRowManufacturerName(Element):
    """
    SubRowManufacturerName
    """
    tag = 'SubRowManufacturerName'


class SubRowNormalProposedAccountIdentifier(Element):
    """
    SubRowNormalProposedAccountIdentifier
    """
    tag = 'SubRowNormalProposedAccountIdentifier'


class SubRowPriceListIdentifier(Element):
    """
    SubRowPriceListIdentifier
    """
    tag = 'SubRowPriceListIdentifier'


class SubRowRequestOfQuotationIdentifier(Element):
    """
    SubRowRequestOfQuotationIdentifier
    """
    tag = 'SubRowRequestOfQuotationIdentifier'


class SubRowShortProposedAccountIdentifier(Element):
    """
    SubRowShortProposedAccountIdentifier
    """
    tag = 'SubRowShortProposedAccountIdentifier'


class SubRowVatAmount(Element):
    """
    SubRowVatAmount
    """
    tag = 'SubRowVatAmount'


class SubRowVatExcludedAmount(Element):
    """
    SubRowVatExcludedAmount
    """
    tag = 'SubRowVatExcludedAmount'


class SubRowVatRatePercent(Element):
    """
    SubRowVatRatePercent
    """
    tag = 'SubRowVatRatePercent'


class SubRowWaybillIdentifier(Element):
    """
    SubRowWaybillIdentifier
    """
    tag = 'SubRowWaybillIdentifier'


class SubArticleIdentifier(Element):
    """
    SubArticleIdentifier
    """
    tag = 'SubArticleIdentifier'


class SubArticleName(Element):
    """
    SubArticleName
    """
    tag = 'SubArticleName'


class SubRowDeliveryDetails(Element):
    """
    SubRowDeliveryDetails
    """
    tag = 'SubRowDeliveryDetails'
    aggregate = [
        SubRowWaybillIdentifier,
        SubRowDelivererIdentifier,
        SubRowDelivererName,
        SubRowDelivererName,
        SubRowDelivererCountryCode,
        SubRowDelivererCountryName,
        SubRowManufacturerIdentifier,
        SubRowManufacturerName,
        SubRowManufacturerCountryCode,
        SubRowManufacturerCountryName, ]


class SubInvoiceRow(Element):
    """
    SubInvoiceRow
    """
    tag = 'SubInvoiceRow'
    aggregate = [
        SubArticleIdentifier,
        SubArticleName,
        SubRowIdentifier,
        SubRowIdentifierDate,
        SubOriginalInvoiceNumber,
        SubRowDeliveryIdentifier,
        SubRowDeliveryDate,
        SubRowAgreementIdentifier,
        SubRowRequestOfQuotationIdentifier,
        SubRowPriceListIdentifier,
        SubRowDeliveryDetails,
        SubRowShortProposedAccountIdentifier,
        SubRowNormalProposedAccountIdentifier,
        SubRowAccountDimensionText,
        SubRowVatRatePercent,
        SubRowVatAmount,
        SubRowVatExcludedAmount,
        SubRowAmount]
