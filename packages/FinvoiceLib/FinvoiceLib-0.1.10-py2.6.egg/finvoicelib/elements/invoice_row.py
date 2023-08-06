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


from finvoicelib.elements import CurrencyElement
from finvoicelib.elements import DateElement
from finvoicelib.elements import DecimalElement
from finvoicelib.elements import Element


class ArticleIdentifier(Element):
    """
    ArticleIdentifier
    """
    tag = 'ArticleIdentifier'


class ArticleInfoUrlText(Element):
    """
    ArticleInfoUrlText
    """
    tag = 'ArticleInfoUrlText'


class ArticleName(Element):
    """
    ArticleName
    """
    tag = 'ArticleName'


class DeliveredQuantity(Element):
    """
    DeliveredQuantity
    """
    tag = 'DeliveredQuantity'

    def set_attributes(self):
        self.attributes = {'quantityunitcode': ''}


class OrderedQuantity(Element):
    """
    OrderedQuantity
    """
    tag = 'OrderedQuantity'

    def set_attributes(self):
        self.attributes = {'quantityunitcode': ''}


class ConfirmedQuantity(Element):
    """
    OrderedQuantity
    """
    tag = 'ConfirmedQuantity'

    def set_attributes(self):
        self.attributes = {'quantityunitcode': ''}


class UnitPriceAmount(CurrencyElement):
    """
    UnitPriceAmount
    """
    tag = 'UnitPriceAmount'


class RowAccountDimensionText(Element):
    """
    RowAccountDimensionText
    """
    tag = 'RowAccountDimensionText'


class RowAgreementIdentifier(Element):
    """
    RowAgreementIdentifier
    """
    tag = 'RowAgreementIdentifier'


class RowAmount(CurrencyElement):
    """
    RowAmount
    """
    tag = 'RowAmount'


class RowDelivererCountryCode(Element):
    """
    RowDelivererCountryCode
    """
    tag = 'RowDelivererCountryCode'


class RowDelivererCountryName(Element):
    """
    RowDelivererCountryName
    """
    tag = 'RowDelivererCountryName'


class RowDelivererIdentifier(Element):
    """
    RowDelivererIdentifier
    """
    tag = 'RowDelivererIdentifier'


class RowDelivererName(Element):
    """
    RowDelivererName
    """
    tag = 'RowDelivererName'


class RowDeliveryDate(DateElement):
    """
    RowDeliveryDate
    """
    tag = 'RowDeliveryDate'


class RowDiscountPercent(Element):
    """
    RowDiscountPercent
    """
    tag = 'RowDiscountPercent'


class RowFreeText(Element):
    """
    RowFreeText
    """
    tag = 'RowFreeText'


class RowIdentifier(Element):
    """
    RowIdentifier
    """
    tag = 'RowIdentifier'


class RowIdentifierDate(DateElement):
    """
    RowIdentifierDate
    """
    tag = 'RowIdentifierDate'


class RowManufacturerCountryCode(Element):
    """
    RowManufacturerCountryCode
    """
    tag = 'RowManufacturerCountryCode'


class RowManufacturerCountryName(Element):
    """
    RowManufacturerCountryName
    """
    tag = 'RowManufacturerCountryName'


class RowManufacturerIdentifier(Element):
    """
    RowManufacturerIdentifier
    """
    tag = 'RowManufacturerIdentifier'


class RowManufacturerName(Element):
    """
    RowManufacturerName
    """
    tag = 'RowManufacturerName'


class RowNormalProposedAccountIdentifier(Element):
    """
    RowNormalProposedAccountIdentifier
    """
    tag = 'RowNormalProposedAccountIdentifier'


class RowPriceListIdentifier(Element):
    """
    RowPriceListIdentifier
    """
    tag = 'RowPriceListIdentifier'


class RowRequestOfQuotationIdentifier(Element):
    """
    RowRequestOfQuotationIdentifier
    """
    tag = 'RowRequestOfQuotationIdentifier'


class RowShortProposedAccountIdentifier(Element):
    """
    RowShortProposedAccountIdentifier
    """
    tag = 'RowShortProposedAccountIdentifier'


class RowSubIdentifier(Element):
    """
    RowSubIdentifier
    """
    tag = 'RowSubIdentifier'


class RowVatAmount(CurrencyElement):
    """
    RowVatAmount
    """
    tag = 'RowVatAmount'


class RowVatExcludedAmount(CurrencyElement):
    """
    RowVatExcludedAmount
    """
    tag = 'RowVatExcludedAmount'


class RowVatRatePercent(DecimalElement):
    """
    RowVatRatePercent
    """
    tag = 'RowVatRatePercent'


class RowWaybillIdentifier(Element):
    """
    RowWaybillIdentifier
    """
    tag = 'RowWaybillIdentifier'


class RowDeliveryDetails(Element):
    """
    RowDeliveryDetails
    """
    tag = 'RowDeliveryDetails'
    aggregate = [
        RowWaybillIdentifier,
        RowDelivererIdentifier,
        RowDelivererName,
        RowDelivererName,
        RowDelivererCountryCode,
        RowDelivererCountryName,
        RowManufacturerIdentifier,
        RowManufacturerName,
        RowManufacturerCountryCode,
        RowManufacturerCountryName]


class InvoiceRow(Element):
    """
    InvoiceRow
    """
    tag = 'InvoiceRow'
    aggregate = [
        RowSubIdentifier,
        ArticleIdentifier,
        ArticleName,
        DeliveredQuantity,
        OrderedQuantity,
        ConfirmedQuantity,
        UnitPriceAmount,
        RowIdentifier,
        RowIdentifierDate,
        RowDeliveryDate,
        RowAgreementIdentifier,
        RowRequestOfQuotationIdentifier,
        RowPriceListIdentifier,
        RowDeliveryDetails,
        RowShortProposedAccountIdentifier,
        RowNormalProposedAccountIdentifier,
        RowFreeText,
        RowVatRatePercent,
        RowVatAmount,
        RowVatExcludedAmount,
        RowAmount]
