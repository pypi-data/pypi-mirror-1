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


import datetime
from decimal import Decimal

from finvoicelib.reader import Reader
from finvoicelib.tests import FinvoiceTestCase
from finvoicelib.wrapper import FinvoiceWrapper


class TestFinvoiceWrapperWithPulliFinvoice(FinvoiceTestCase):

    """
    TestFinvoiceWrapper(WithPulliFinvoice)

    Contains the test suite for the module finvoice.wrapper and acts as a
    documentation for the FinvoiceWrapper.

    """

    def setUp(self):
        """
        Set up the FinvoiceWrapper

        FinvoiceWrapper essentially wraps the most used elements of the
        finvoice payload to a convinient class.
        """

        # Reader only accepts file-like objects
        reader = Reader(self.get_pulli_finvoice())

        # Get first message from the file.
        msg = reader.messages[0]

        self.wrapper = FinvoiceWrapper(msg)

    def test_payee_name(self):
        """
        test_payee_name

        payee.name carries the value from the first <SellerOrganisationName>
        element.

        """
        payee = self.wrapper.payee
        self.assertEqual(payee.name, 'Pullin Musiikki Oy')

    def test_payee_business_id(self):
        """
        test_payee_business_id

        payee.business_id carries the business id of the seller party. This
        field can be empty if the business_id wasn't declared or it had
        a invalid value.

        """
        payee = self.wrapper.payee
        self.assertEqual(str(payee.business_id), '0199920-7')

    def test_payee_bank_account_number(self):
        """
        test_payee_bank_account_number
        """
        payee = self.wrapper.payee
        self.assertEqual(str(payee.bank_account_number), '500015-20000081')

    def test_payee_address(self):
        """
        test_payee_address

        payee.postal_address contain the collected values from the
        SellerPostalAddressDetails aggregate.

        """
        address = self.wrapper.payee.postal_address
        self.assertEqual(address.street_name, 'Puukatu 2 F')
        self.assertEqual(address.postal_code, '00112')
        self.assertEqual(address.city, 'HELSINKI')
        self.assertEqual(address.country, '')

    def test_payee_bank_swift_code(self):
        """
        test_payee_bank_swift_code

        """
        payee = self.wrapper.payee
        self.assertEqual(str(payee.bank_swift_code), 'OKOYFIHH')

    def test_payee_contact_email(self):
        """
        test_payee_contact_email
        """
        payee = self.wrapper.payee
        self.assertEqual(payee.contact_email,
            'hanna.paananen@pullinmusiikki.fi')

    def test_payee_contact_name(self):
        """
        test_payee_contact_name
        """
        payee = self.wrapper.payee
        self.assertEqual(payee.contact_name, 'Hanna Paananen')

    def test_payee_contact_phone(self):
        """
        test_payee_contact_phone
        """
        payee = self.wrapper.payee
        self.assertEqual(payee.contact_phone, '09-3213212')

    def test_payee_iban_account_number(self):
        """
        test_payee_iban_account_number

        """
        # TODO: unimplemented
        payee = self.wrapper.payee
        self.assertEqual(payee.iban_account_number, '')

    def test_payee_website(self):
        """
        test_payee_contact_phone
        """
        payee = self.wrapper.payee
        self.assertEqual(payee.website, 'www.pullinmusiikki.fi')

    def test_payee_organisation_unit_number(self):
        """
        test_payee_contact_phone
        """
        payee = self.wrapper.payee
        self.assertEqual(payee.organisation_unit_number, '003701999207')

    def test_payee_organisation_taxcode(self):
        """
        test_payee_contact_phone
        """
        payee = self.wrapper.payee
        self.assertEqual(payee.organisation_taxcode, '0199920-7')

    def test_payee_bank_accounts(self):
        """
        test_payee_contact_phone
        """
        payee = self.wrapper.payee
        self.assertEqual(len(payee.bank_accounts), 3)

        self.assertEqual(payee.bank_accounts[0].account_number,
                         'FI2757800750155448')
        self.assertEqual(payee.bank_accounts[0].swift_code, 'OKOYFIHH')

        self.assertEqual(payee.bank_accounts[1].account_number,
                         'FI2721221222212227')
        self.assertEqual(payee.bank_accounts[1].swift_code, 'NDEAFIHH')

        self.assertEqual(payee.bank_accounts[2].account_number,
                         'FI2781232323312334')
        self.assertEqual(payee.bank_accounts[2].swift_code, 'PSPBFIHH')

    def test_payer_name(self):
        """
        test_payer_name

        payer.name carries the value from the first <BuyerOrganisationName>
        element.

        """
        payer = self.wrapper.payer
        self.assertEqual(payer.name, 'Sensorit Oy')

    def test_payer_net_service_id(self):
        """
        test_payer_net_service_id

        payer.net_service_id contains the buyer's party id from the
        SOAP-ENVELOPE.

        """
        payer = self.wrapper.payer
        self.assertEqual(payer.net_service_id, '')

    def test_payer_business_id(self):
        """
        test_payer_business_id

        payer.business_id carries the business id of the buyer party. This
        field can be empty if the business id wasn't declared or it had
        a invalid value.

        """
        payer = self.wrapper.payer
        self.assertEqual(str(payer.business_id), '1234567-1')

    def test_payer_address(self):
        """
        test_payer_address

        payer.postal_address contain the collected values from the
        BuyerPostalAddressDetails aggregate.
        """
        address = self.wrapper.payer.postal_address
        self.assertEqual(address.street_name, 'Sempalokatu 2')
        self.assertEqual(address.postal_code, '00122')
        self.assertEqual(address.city, 'HELSINKI')
        self.assertEqual(address.country, '')

    def test_payer_contact_name(self):
        """
        test_payer_contact_name
        """
        payer = self.wrapper.payer
        self.assertEqual(payer.contact_name, 'Hannes Puumalainen')

    def test_payer_contact_email(self):
        """
        test_payer_contact_email

        """
        payer = self.wrapper.payer
        self.assertEqual(str(payer.contact_email),
            'hannes.puumalainen@sensorit.fi')

    def test_payer_customer_number(self):
        """
        test_payer_customer_number
        """
        payer = self.wrapper.payer
        self.assertEqual(payer.customer_number, '1122')

    def test_payer_contact_phone(self):
        """
        test_payer_contact_phone

        """
        payer = self.wrapper.payer
        self.assertEqual(str(payer.contact_phone), '050-543 2658')

    def test_payer_organisation_unit_number(self):
        """
        test_payer_contact_phone

        """
        payer = self.wrapper.payer
        self.assertEqual(str(payer.organisation_unit_number), '00371234567')

    def test_payer_organisation_taxcode(self):
        """
        test_payer_contact_phone

        """
        payer = self.wrapper.payer
        self.assertEqual(str(payer.organisation_taxcode), 'FI12345671')

    def test_invoice_total_taxed(self):
        """
        test_invoice_total_taxed

        invoice.total_taxed carries the value from the element
        <InvoiceTotalVatIncludedAmount>.

        invoice.total_taxed_currency has the currency code declared in the
        element by the attribute AmountCurrencyIdentifier.

        """
        invoice = self.wrapper.invoice
        self.assertEqual(invoice.total_taxed, Decimal('3352.98'))
        self.assertEqual(invoice.total_taxed_currency, 'EUR')

    def test_invoice_total_untaxed(self):
        """
        test_invoice_total_untaxed

        invoice.total_untaxed carries the value from the element
        <InvoiceTotalVatExcludedAmount>.

        invoice.total_untaxed_currency has the currency code declared in the
        element by the attribute AmountCurrencyIdentifier.

        """
        invoice = self.wrapper.invoice
        self.assertEqual(invoice.total_untaxed, Decimal('2830.30'))
        self.assertEqual(invoice.total_untaxed_currency, 'EUR')

    def test_invoice_vat_amount(self):
        """
        test_invoice_vat_amount

        invoice.vat_amount carries the value from the element
        <InvoiceTotalVatAmount>.

        invoice.vat_amount_currency has the currency code declared in the
        element by the attribute AmountCurrencyIdentifier.

        """
        invoice = self.wrapper.invoice
        self.assertEqual(invoice.vat_amount, Decimal('622.68'))
        self.assertEqual(invoice.vat_amount_currency, 'EUR')

    def test_invoice_number(self):
        """
        test_invoice_number
        """
        invoice = self.wrapper.invoice
        self.assertEqual(invoice.number, '159')

    def test_invoice_free_text(self):
        """
        test_invoice_free_text

        invoice.free_text has the combined values from all the
        <InvoiceFreeText> elements.

        """
        invoice = self.wrapper.invoice
        self.assertEqual(invoice.free_text,
                         u'Vapaata tekstiä enintään 512 merkkiä')

    def test_invoice_overdue_percent(self):
        """
        test_invoice_overdue_percent
        """
        invoice = self.wrapper.invoice
        self.assertEqual(invoice.payment_overdue_percent, '16')

    def test_invoice_overdue_freetext(self):
        """
        test_invoice_overdue_freetext

        Element: <PaymentOverDueFineFreeText>
        """
        invoice = self.wrapper.invoice
        self.assertEqual(invoice.payment_overdue_text, u'Viivästyskorko 16%')

    def test_invoice_terms_of_payment(self):
        """
        test_invoice_terms_of_payment

        """
        invoice = self.wrapper.invoice
        self.assertEqual(invoice.terms_of_payment, (u'5 pävää ./.2%,'
                                                    u' 14 päivää netto'))

    def test_invoice_typecode(self):
        """
        test_invoice_typecode

        """
        invoice = self.wrapper.invoice
        self.assertEqual(invoice.typecode, u'INV01')

    def test_invoice_type_text(self):
        """
        test_invoice_type_text

        """
        invoice = self.wrapper.invoice
        self.assertEqual(invoice.type_text, u'LASKU')

    def test_rows_len(self):
        """
        test_rows_len

        All the <InvoiceRow> -elements are collected to the list: rows.

        """
        rows = self.wrapper.rows
        self.assertEqual(len(rows), 8)

    def test_rows_0(self):
        """
        test_rows_0

        Demonstrates the available attibutes of a row.
        """
        row = self.wrapper.rows[0]
        self.assertEqual(row.name, 'TUURA')
        self.assertEqual(row.article_identifier, '123123')
        self.assertEqual(row.quantity, Decimal('10'))
        self.assertEqual(row.unit_price, Decimal('28.69'))
        self.assertEqual(row.total_taxed, Decimal("350.02"))
        self.assertEqual(row.total_taxed_currency, 'EUR')
        self.assertEqual(row.total_untaxed, Decimal('286.90'))
        self.assertEqual(row.total_untaxed_currency, 'EUR')
        self.assertEqual(row.vat_amount, Decimal("63.12"))
        self.assertEqual(row.vat_amount_currency, 'EUR')
        self.assertEqual(row.vat_percent, Decimal('22'))
        self.assertEqual(row.unit_code, 'kpl')
        self.assertEqual(row.freetext,
            u'Tuote myydään varsien ja ohjeen kanssa.\n')
        self.assertEqual(row.date, datetime.date(2004, 12, 13))

    def test_rows_1(self):
        """
        test_rows_1

        Demonstrates the available attibutes of a row.
        """
        row = self.wrapper.rows[1]
        self.assertEqual(row.name, 'Tussi')
        self.assertEqual(row.article_identifier, '8768217637')
        self.assertEqual(row.quantity, Decimal('120'))
        self.assertEqual(row.unit_price, Decimal('1.64'))
        self.assertEqual(row.total_taxed, Decimal("240.10"))
        self.assertEqual(row.total_taxed_currency, 'EUR')
        self.assertEqual(row.total_untaxed, Decimal('196.80'))
        self.assertEqual(row.total_untaxed_currency, 'EUR')
        self.assertEqual(row.vat_amount, Decimal("43.30"))
        self.assertEqual(row.vat_amount_currency, 'EUR')
        self.assertEqual(row.vat_percent, Decimal('22'))
        self.assertEqual(row.unit_code, 'kpl')

    def test_rows_2(self):
        """
        test_rows_1

        Demonstrates the available attibutes of a row.
        """
        row = self.wrapper.rows[2]
        self.assertEqual(row.name, '')
        self.assertEqual(row.article_identifier, '')
        self.assertEqual(row.quantity, None)
        self.assertEqual(row.unit_price, None)
        self.assertEqual(row.total_taxed, None)
        self.assertEqual(row.total_taxed_currency, None)
        self.assertEqual(row.total_untaxed, None)
        self.assertEqual(row.total_untaxed_currency, None)
        self.assertEqual(row.vat_amount, None)
        self.assertEqual(row.vat_amount_currency, None)
        self.assertEqual(row.vat_percent, None)
        self.assertEqual(row.unit_code, None)

    def test_delivery_party_contact_email(self):
        """
        test_invoice_delivery_contact_email

        invoice.delivery_contact_email contains the value from the element
        <DeliveryEmailaddressIdentifier>.
        """
        delivery_party = self.wrapper.delivery_party
        self.assertEqual(delivery_party.contact_email,
            'maija.vilkkunen@kolumbus.fi')

    def test_delivery_party_contact_name(self):
        """
        test_invoice_delivery_contact_email

        invoice.delivery_contact_name contains the value from the element
        <DeliveryContactName>.
        """
        delivery_party = self.wrapper.delivery_party
        self.assertEqual(delivery_party.contact_name, 'Maija Vilkkunen')

    def test_delivery_party_contact_phone(self):
        """
        test_invoice_delivery_contact_phone

        invoice.delivery_contact_phone contains the value from the element
        <DeliveryPhoneNumberIdentifier>.

        """
        delivery_party = self.wrapper.delivery_party
        self.assertEqual(delivery_party.contact_phone, '09-123 12345')

    def test_delivery_party_delivery_date(self):
        """
        test_invoice_delivery_date

        invoice.delivery_contact_phone contains the value from the element
        <DeliveryDate>.

        """
        delivery_party = self.wrapper.delivery_party
        self.assertEqual(delivery_party.delivery_date,
            datetime.date(2004, 12, 5))

    def test_delivery_party_delivery_method(self):
        """
        test_invoice_delivery_date

        """
        delivery_party = self.wrapper.delivery_party
        self.assertEqual(delivery_party.delivery_method, 'Noudetaan')

    def test_delivery_party_name(self):
        """
        test_invoice_delivery_organisation_name

        invoice.delivery_contact_phone contains the value from the
        <DeliveryOrganisationName> element.
        """
        delivery_party = self.wrapper.delivery_party
        self.assertEqual(delivery_party.name, u'Helsingin Tanssihalli')

    def test_delivery_party_address(self):
        """
        test_delivery_party_address

        delivery_party.address contain the collected values from the
        DeliveryPostalAddressDetails aggregate.
        """
        delivery_address = self.wrapper.delivery_party.address
        self.assertEqual(delivery_address.street_name, 'Satamakatu 2')
        self.assertEqual(delivery_address.postal_code, '00100')
        self.assertEqual(delivery_address.city, 'Helsinki')
        self.assertEqual(delivery_address.country, '')
        self.assertEqual(delivery_address.post_office_box, '')

    def test_delivery_party_name(self):
        """
        test_invoice_delivery_organisation_name

        invoice.delivery_contact_phone contains the value from the
        <DeliveryOrganisationName> element.
        """
        invoice_recipient = self.wrapper.invoice_recipient
        self.assertEqual(invoice_recipient.organisation_name, u'Tilitoimisto Ryynänen')

    def test_invoice_recipient_party_address(self):
        """
        test_delivery_party_address

        delivery_party.address contain the collected values from the
        DeliveryPostalAddressDetails aggregate.
        """
        invoice_recipient = self.wrapper.invoice_recipient.address
        self.assertEqual(invoice_recipient.street_name, u'Mäkelänkatu 2')
        self.assertEqual(invoice_recipient.postal_code, '00102')
        self.assertEqual(invoice_recipient.city, 'Helsinki')
        self.assertEqual(invoice_recipient.country, 'FINLAND')
        self.assertEqual(invoice_recipient.post_office_box, 'PL 22')

class TestFinvoiceWrapperWithPankkiyhdistysFinvoice(FinvoiceTestCase):
    """
    TestFinvoiceWrapper(WithPankkiyhdistysFinvoice)

    Contains the test suite for the module finvoice.wrapper and acts as a
    documentation for the FinvoiceWrapper.

    """

    def setUp(self):
        """
        Set up the FinvoiceWrapper

        FinvoiceWrapper essentially wraps the most used elements of the
        finvoice payload to a convinient class.
        """

        # Reader only accepts file-like objects
        reader = Reader(self.get_pankkiyhdistys_finvoice())

        # Get first message from the file.
        msg = reader.messages[0]

        self.wrapper = FinvoiceWrapper(msg)

    def test_payee_name(self):
        """
        test_payee_name

        payee.name carries the value from the first <SellerOrganisationName>
        element.

        """
        payee = self.wrapper.payee
        self.assertEqual(payee.name, 'Pullin Kala')

    def test_payee_business_id(self):
        """
        test_payee_business_id

        payee.business_id carries the business id of the seller party. This
        field can be empty if the business_id wasn't declared or it had
        a invalid value.

        """
        payee = self.wrapper.payee
        self.assertEqual(payee.business_id, '')

    def test_payer_name(self):
        """
        test_payer_name

        payer.name carries the value from the first <BuyerOrganisationName>
        element.

        """
        payer = self.wrapper.payer
        self.assertEqual(payer.name, 'Kalakauppa Vilkkunen')

    def test_payer_net_service_id(self):
        """
        test_payer_net_service_id
        """
        payer = self.wrapper.payer
        self.assertEqual(payer.net_service_id, 'FI3329501800008512')

    def test_payee_net_service_id(self):
        """
        test_payee_net_service_id
        """
        payee = self.wrapper.payee
        self.assertEqual(payee.net_service_id, 'FI9859292720000267')
