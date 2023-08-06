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
from finvoicelib.elements import Element
from finvoicelib.elements.seller import SellerReferenceIdentifier


class InvoiceDate(DateElement):
    """
    InvoiceDate
    """
    tag = 'InvoiceDate'


class InvoiceTypeCode(Element):
    """
    InvoiceTypeCode
    """
    tag = 'InvoiceTypeCode'


class InvoiceTypeText(Element):
    """
    InvoiceTypeText
    """
    tag = 'InvoiceTypeText'


class OriginCode(Element):
    """
    OriginCode
    """
    tag = 'OriginCode'


class InvoiceDueDate(DateElement):
    """
    InvoiceDueDate
    """
    tag = 'InvoiceDueDate'


class InvoiceNumber(Element):
    """
    InvoiceNumber
    """
    tag = 'InvoiceNumber'


class InvoiceSenderOrganisationName(Element):
    """
    InvoiceSenderOrganisationName
    """
    tag = 'InvoiceSenderOrganisationName'


class InvoiceSenderPartyIdentifier(Element):
    """
    InvoiceSenderPartyIdentifier
    """
    tag = 'InvoiceSenderPartyIdentifier'


class InvoiceTotalVatAmount(CurrencyElement):
    """
    InvoiceTotalVatAmount
    """
    tag = 'InvoiceTotalVatAmount'


class InvoiceTotalVatExcludedAmount(CurrencyElement):
    """
    InvoiceTotalVatExcludedAmount
    """
    tag = 'InvoiceTotalVatExcludedAmount'


class InvoiceTotalVatIncludedAmount(CurrencyElement):
    """
    InvoiceTotalVatIncludedAmount
    """
    tag = 'InvoiceTotalVatIncludedAmount'


class InvoiceTypeCode(Element):
    """
    InvoiceTypeCode
    """
    tag = 'InvoiceTypeCode'


class InvoiceTypeText(Element):
    """
    InvoiceTypeText
    """
    tag = 'InvoiceTypeText'


class InvoiceUrlNameText(Element):
    """
    InvoiceUrlNameText
    """
    tag = 'InvoiceUrlNameText'


class InvoiceUrlText(Element):
    """
    InvoiceUrlText
    """
    tag = 'InvoiceUrlText'


class VatBaseAmount(Element):
    """
    VatBaseAmount
    """
    tag = 'VatBaseAmount'


class VatRateAmount(Element):
    """
    VatRateAmount
    """
    tag = 'VatRateAmount'


class VatRatePercent(Element):
    """
    VatRatePercent
    """
    tag = 'VatRatePercent'


class VatSpecificationDetails(Element):
    """
    VatSpecificationDetails
    """
    tag = 'VatSpecificationDetails'
    aggregate = [VatBaseAmount, VatRatePercent, VatRateAmount]


class OrderIdentifier(Element):
    """
    OrderIdentifier
    """
    tag = 'OrderIdentifier'


class BuyerReferenceIdentifier(Element):
    """
    Finvoice 1.3
    BuyerReferenceIdentifier
    """
    tag = 'BuyerReferenceIdentifier'


class OrderIdentifier(Element):
    """
    OrderIdentifier
    """
    tag = 'OrderIdentifier'

class InvoiceSenderPartyDetails(Element):
    """
    InvoiceSenderPartyDetails
    """
    tag = 'InvoiceSenderPartyDetails'
    aggregate = [InvoiceSenderPartyIdentifier,
        InvoiceSenderOrganisationName,
        InvoiceSenderOrganisationName]


class CashDiscountAmount(Element):
    """
    CashDiscountAmount
    """
    tag = 'CashDiscountAmount'


class CashDiscountBaseAmount(Element):
    """
    CashDiscountBaseAmount
    """
    tag = 'CashDiscountBaseAmount'


class CashDiscountDate(DateElement):
    """
    CashDiscountDate
    """
    tag = 'CashDiscountDate'


class CashDiscountPercent(Element):
    """
    CashDiscountPercent
    """
    tag = 'CashDiscountPercent'


class PaymentTermsFreeText(Element):
    """
    PaymentTermsFreeText
    """
    tag = 'PaymentTermsFreeText'


class PaymentOverDueFineFreeText(Element):
    """
    PaymentOverDueFineFreeText
    """
    tag = 'PaymentOverDueFineFreeText'


class PaymentOverDueFinePercent(Element):
    """
    PaymentOverDueFinePercent
    """
    tag = 'PaymentOverDueFinePercent'


class PaymentStatusCode(Element):
    """
    PaymentStatusCode
    """
    tag = 'PaymentStatusCode'


class PaymentStatusDetails(Element):
    """
    PaymentStatusDetails
    """
    tag = 'PaymentStatusDetails'
    aggregate = [PaymentStatusCode]


class PaymentOverDueFineDetails(Element):
    """
    PaymentOverDueFineDetails
    """
    tag = 'PaymentOverDueFineDetails'
    aggregate = [PaymentOverDueFineFreeText, PaymentOverDueFinePercent]


class InvoiceFreeText(Element):
    """
    InvoiceFreeText
    """
    tag = 'InvoiceFreeText'


class PaymentTermsDetails(Element):
    """
    PaymentTermsDetails
    """
    tag = 'PaymentTermsDetails'
    aggregate = [
        PaymentTermsFreeText,
        InvoiceDueDate,
        CashDiscountDate,
        CashDiscountBaseAmount,
        CashDiscountPercent,
        CashDiscountAmount,
        PaymentOverDueFineDetails]


class InvoiceDetails(Element):
    """
    InvoiceDetails
    """
    tag = 'InvoiceDetails'
    aggregate = [
        InvoiceTypeCode,
        InvoiceTypeText,
        OriginCode,
        InvoiceNumber,
        InvoiceDate,
        InvoiceFreeText,
        SellerReferenceIdentifier,
        BuyerReferenceIdentifier,
        OrderIdentifier,
        InvoiceTotalVatExcludedAmount,
        InvoiceTotalVatAmount,
        InvoiceTotalVatIncludedAmount,
        VatSpecificationDetails,
        PaymentTermsDetails]


class VirtualBankBarcode(Element):
    """
    VirtualBankBarcode
    """
    tag = 'VirtualBankBarcode'
