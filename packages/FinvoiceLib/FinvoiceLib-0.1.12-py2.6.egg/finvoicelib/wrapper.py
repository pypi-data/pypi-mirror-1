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

from business_tools import BusinessID
from decimal import Decimal
from finvoicelib.error import ValueMismatchError
from finvoicelib.error import VersionWarning


class _Decimal(Decimal):

    def __new__(cls, * args, ** kwargs):
        value = args[0].replace(',', '.')
        args = (value, ) + args[1:]
        obj = Decimal.__new__(cls, * args, ** kwargs)
        return obj


class Invoice(object):

    number = None
    date = None
    due_date = None
    reference = None
    total_taxed = None
    total_untaxed = None
    vat_amount = None
    total_taxed_currency = None
    total_untaxed_currency = None
    vat_amount_currency = None
    free_text = None
    terms_of_payment = None
    payment_overdue_text = None
    payment_overdue_percent = None
    typecode = None
    type_text = None
    order_identifier = None
    seller_reference_identifier = None
    buyer_reference_identifier = None

    def set_epi_details(self, doc):
        epi_details = doc.EpiDetailsSet
        if len(epi_details) > 0:
            epi_payment_details = \
                epi_details[0].EpiPaymentInstructionDetailsSet
            if len(epi_payment_details) > 0:
                epi_reference = \
                    epi_payment_details[0].EpiRemittanceInfoIdentifierSet
                if len(epi_reference):
                    self.reference = epi_reference[0].text

    def set_invoice_details(self, doc):
        invoice_details = doc.InvoiceDetailsSet
        if len(invoice_details) > 0:
            typecode = invoice_details[0].InvoiceTypeCodeSet
            if len(typecode) > 0:
                self.typecode = typecode[0].text
            type_text = invoice_details[0].InvoiceTypeTextSet
            if len(type_text) > 0:
                self.type_text = type_text[0].text
            number = invoice_details[0].InvoiceNumberSet
            if len(number) > 0:
                self.number = number[0].text

            date = invoice_details[0].InvoiceDateSet
            if len(date) > 0:
                if date[0].text:
                    self.date = date[0].text

            payment_details = invoice_details[0].PaymentTermsDetailsSet
            if len(payment_details) > 0:
                terms = payment_details[0].PaymentTermsFreeTextSet
                if len(terms)>0 and terms[0].text:
                    self.terms_of_payment = terms[0].text
                due_date = payment_details[0].InvoiceDueDateSet
                if len(due_date) > 0:
                    if due_date[0].text:
                        self.due_date = due_date[0].text
                fine_details = payment_details[0].PaymentOverDueFineDetailsSet
                if len(fine_details) > 0:
                    overdue_text = \
                        fine_details[0].PaymentOverDueFineFreeTextSet
                    if len(overdue_text) > 0:
                        self.payment_overdue_text = overdue_text[0].text
                    payment_overdue_percent = \
                        fine_details[0].PaymentOverDueFinePercentSet
                    if len(payment_overdue_percent) > 0:
                        self.payment_overdue_percent = \
                            payment_overdue_percent[0].text

            total_untaxed = invoice_details[0].InvoiceTotalVatExcludedAmountSet
            if len(total_untaxed) > 0:
                self.total_untaxed = _Decimal(total_untaxed[0].text)
                currency = \
                    total_untaxed[0].attributes.get('amountcurrencyidentifier',
                                                    '')
                self.total_untaxed_currency = currency

            total_taxed = invoice_details[0].InvoiceTotalVatIncludedAmountSet
            if len(total_taxed) > 0:
                self.total_taxed = _Decimal(total_taxed[0].text)
                self.total_taxed_currency = \
                    total_taxed[0].attributes.get('amountcurrencyidentifier',
                                                  '')

            vat_amount = invoice_details[0].InvoiceTotalVatAmountSet
            if len(vat_amount) > 0:
                self.vat_amount = _Decimal(vat_amount[0].text)
                self.vat_amount_currency = \
                    vat_amount[0].attributes.get('amountcurrencyidentifier',
                                                 '')

            order_identifier = invoice_details[0].OrderIdentifierSet
            if len(order_identifier) > 0:
                self.order_identifier = order_identifier[0].text

            seller_reference_identifier = invoice_details[0].SellerReferenceIdentifierSet
            if len(seller_reference_identifier) > 0:
                self.seller_reference_identifier = seller_reference_identifier[0].text

            buyer_reference_identifier = invoice_details[0].BuyerReferenceIdentifierSet
            if len(buyer_reference_identifier) > 0:
                self.buyer_reference_identifier = buyer_reference_identifier[0].text

            free_text = invoice_details[0].InvoiceFreeTextSet
            if len(free_text) > 0:
                self.free_text = free_text.as_string(delim='\n')

    def __init__(self, doc):

        self.set_epi_details(doc)
        self.set_invoice_details(doc)


class PostalAddress(object):
    street_name = ''
    postal_code = ''
    city = ''
    country = ''
    country_code = ''
    post_office_box = ''
    node_prefix = ''

    def __init__(self, element_node=None):
        if not element_node:
            self.street_name = ''
            self.postal_code = ''
            self.city = ''
            self.country = ''
            self.country_code = ''
            self.post_office_box = ''
            return

        name = self.node_prefix + 'StreetName'
        street_name = element_node.get_children_by_name(name)
        if street_name:
            self.street_name = street_name[0].text or ''

        name = self.node_prefix + 'TownName'
        city = element_node.get_children_by_name(name)
        if city:
            self.city = city[0].text or ''

        name = self.node_prefix + 'PostCodeIdentifier'
        postal_code = element_node.get_children_by_name(name)
        if postal_code:
            self.postal_code = postal_code[0].text or ''

        country_code = element_node.get_children_by_name('CountryCode')
        if country_code:
            self.country_code = country_code[0].text or ''

        country = element_node.get_children_by_name('CountryName')
        if country and len(country) > 0:
            self.country = country[0].text or ''

        name = self.node_prefix + 'PostOfficeBoxIdentifier'
        post_office_box = element_node.get_children_by_name(name)
        if post_office_box and len(post_office_box) > 0:
            self.post_office_box = post_office_box[0].text or ''


class SellerPostalAddress(PostalAddress):
    node_prefix = 'Seller'


class BuyerPostalAddress(PostalAddress):
    node_prefix = 'Buyer'


class DeliveryAddress(PostalAddress):
    node_prefix = 'Delivery'

class InvoiceRecipientAddress(PostalAddress):
    node_prefix = 'InvoiceRecipient'

class InvoiceRecipient(object):
    organisation_name = ''
    party_identifier = ''
    tax_code = ''
    address = None
    einvoice_address = ''
    intermediator_address = ''
    
    def __init__(self, doc):
        self.address = InvoiceRecipientAddress()

        invoice_recipient_party_details = doc.InvoiceRecipientPartyDetailsSet
        if len(invoice_recipient_party_details) > 0:
            postal_address = \
                invoice_recipient_party_details[0].InvoiceRecipientPostalAddressDetailsSet
            if len(postal_address) > 0:
                self.address = InvoiceRecipientAddress(postal_address[0])

            party_identifier = \
                invoice_recipient_party_details[0].InvoiceRecipientPartyIdentifierSet
            if len(party_identifier) > 0:
                self.party_identifier = party_identifier[0].text

            organisation_name = \
                invoice_recipient_party_details[0].InvoiceRecipientOrganisationNameSet
            if len(organisation_name) > 0:
                self.organisation_name = organisation_name[0].text

            tax_code = \
                invoice_recipient_party_details[0].InvoiceRecipientOrganisationTaxCodeSet
            if len(tax_code) > 0:
                self.tax_code = organisation_name[0].text

        info_details = doc.SellerInformationDetailsSet
        if len(info_details) > 0:
            invoice_recipient_details = info_details[0].InvoiceRecipientDetailsSet
            if len(invoice_recipient_details) > 0:

                invoice_recipient_einvoice_address = \
                    invoice_recipient_details[0].InvoiceRecipientAddressSet
                if len(invoice_recipient_einvoice_address) > 0:
                    self.einvoice_address = \
                         invoice_recipient_einvoice_address[0].text

                invoice_recipient_intermediator_address = \
                    invoice_recipient_details[0].InvoiceRecipientIntermediatorAddressSet
                if len(invoice_recipient_intermediator_address) > 0:
                    self.intermediator_address = \
                         invoice_recipient_intermediator_address[0].text

class DeliveryParty(object):
    contact_email = ''
    contact_name = ''
    contact_phone = ''
    delivery_date = None
    delivery_method = ''
    name = ''
    address = None

    def __init__(self, doc):

        self.address = DeliveryAddress()
        delivery_contact_person = doc.DeliveryContactPersonNameSet
        if len(delivery_contact_person) > 0:
            self.contact_name = delivery_contact_person[0].text

        delivery_comm_details = doc.DeliveryCommunicationDetailsSet
        if len(delivery_comm_details) > 0:
            email_address = \
                delivery_comm_details[0].DeliveryEmailaddressIdentifierSet
            if len(email_address) > 0:
                self.contact_email = email_address[0].text
            phone = delivery_comm_details[0].DeliveryPhoneNumberIdentifierSet
            if len(phone) > 0:
                self.contact_phone = phone[0].text

        delivery_details = doc.DeliveryDetailsSet
        if len(delivery_details) > 0:
            delivery_date = delivery_details[0].DeliveryDateSet
            if len(delivery_date) > 0:
                self.delivery_date = delivery_date[0].text
            delivery_method = delivery_details[0].DeliveryMethodTextSet
            if len(delivery_method) > 0:
                self.delivery_method = delivery_method[0].text

        delivery_party_details = doc.DeliveryPartyDetailsSet
        if len(delivery_party_details) > 0:
            postal_address = \
                delivery_party_details[0].DeliveryPostalAddressDetailsSet
            if len(postal_address) > 0:
                self.address = DeliveryAddress(postal_address[0])
            organisation_name = \
                delivery_party_details[0].DeliveryOrganisationNameSet
            if len(organisation_name) > 0:
                self.name = organisation_name[0].text


class BankAccount(object):
    swift_code = ''
    account_number = ''

    def __init__(self, account_number, swift_code):
        self.account_number = account_number
        self.swift_code = swift_code


class Payee(object):
    name = ''
    business_id = ''
    postal_address = ''
    net_service_id = ''
    bank_account_number = ''
    bank_swift_code = ''
    contact_email = ''
    contact_name = ''
    contact_phone = ''
    iban_account_number = ''
    phone = ''
    fax = ''
    website = ''
    organisation_unit_number = ''
    organisation_taxcode = ''
    bank_accounts = None
    intermediator = None

    def __init__(self, doc, envelope=None):
        if envelope:
            self.net_service_id = envelope.seller_id
            self.intermediator = envelope.seller_intermediator_id

        self.postal_address = SellerPostalAddress()
        self.delivery_address = DeliveryAddress()
        self.bank_accounts = []
        
        epi = doc.EpiDetailsSet
        if len(epi) > 0:
            party_details = epi[0].EpiPartyDetailsSet
            if len(party_details) > 0:
                beneficiary = party_details[0].EpiBeneficiaryPartyDetailsSet
                if len(beneficiary) > 0:
                    account_id = beneficiary[0].EpiAccountIDSet
                    if len(account_id) > 0:
                        self.bank_account_number = account_id[0].text
                    name = beneficiary[0].EpiNameAddressDetailsSet
                    if len(name) > 0:
                        self.name = name[0].text
                    business_id = beneficiary[0].EpiBeiSet
                    if len(business_id) > 0:
                        self.business_id = business_id[0].text

                bfi = party_details[0].EpiBfiPartyDetailsSet
                if len(bfi) > 0:
                    bfi_id = bfi[0].EpiBfiIdentifierSet
                    if len(bfi_id) > 0:
                        self.bank_swift_code = bfi_id[0].text

        info_details = doc.SellerInformationDetailsSet
        if len(info_details) > 0:
            website = info_details[0].SellerWebaddressIdentifierSet
            if len(website) > 0:
                self.website = website[0].text

            fax = info_details[0].SellerFaxNumberSet
            if len(fax) > 0:
                self.fax = fax[0].text

            for account in info_details[0].SellerAccountDetailsSet:
                account_number = account.SellerAccountIDSet[0].text
                swift_code = account.SellerBicSet[0].text
                acc = BankAccount(account_number, swift_code)
                self.bank_accounts.append(acc)

        org_unit_number = doc.SellerOrganisationUnitNumberSet
        if len(org_unit_number) > 0:
            self.organisation_unit_number = org_unit_number[0].text
            if not self.business_id \
                and str(self.organisation_unit_number).startswith('0037') \
                    and len(self.organisation_unit_number) > 11:
                        business_id = self.organisation_unit_number[4:12]
                        if BusinessID.is_valid(business_id):
                            self.business_id = business_id

        details = doc.SellerPartyDetailsSet
        if len(details) > 0:
            postal_address = details[0].SellerPostalAddressDetailsSet
            if len(postal_address) > 0:
                self.postal_address = SellerPostalAddress(postal_address[0])
            seller = details[0].SellerOrganisationNameSet
            if len(self.name) < 1 and len(seller) > 0:
                self.name = seller[0].text

            taxcode = details[0].SellerOrganisationTaxCodeSet
            if len(taxcode) > 0:
                self.organisation_taxcode = taxcode[0].text
                if not self.business_id:
                    if BusinessID.is_valid(taxcode[0].text):
                        self.business_id = str(BusinessID(taxcode[0].text))

            business_id = details[0].SellerPartyIdentifierSet
            if not self.business_id and len(business_id) > 0 and \
                    business_id[0].text:
                self.business_id = str(business_id[0].text)

        contact_name = doc.SellerContactPersonNameSet
        if len(contact_name) > 0:
            self.contact_name = contact_name[0].text

        comm_details = doc.SellerCommunicationDetailsSet
        if len(comm_details) > 0:
            phone = comm_details[0].SellerPhoneNumberIdentifierSet
            if len(phone) > 0:
                self.contact_phone = phone[0].text
            email = comm_details[0].SellerEmailaddressIdentifierSet
            if len(email) > 0:
                self.contact_email = email[0].text


class Payer(object):

    name = ''
    business_id = ''
    customer_number = None
    postal_address = None
    net_service_id = ''
    #bank_account_number = ''
    #bank_swift_code = ''
    contact_email = ''
    contact_name = ''
    contact_phone = ''
    #iban_account_number = ''
    phone = ''
    #website = ''
    organisation_unit_number = ''
    organisation_taxcode = ''
    intermediator = None

    def __init__(self, doc=None, envelope=None):
        self.net_service_id = ''
        self.postal_address = BuyerPostalAddress()

        if envelope:
            self.net_service_id = envelope.buyer_id
            self.intermediator = envelope.buyer_intermediator_id

        org_unit_number = doc.BuyerOrganisationUnitNumberSet
        if len(org_unit_number) > 0 and org_unit_number[0].text:
            self.organisation_unit_number = org_unit_number[0].text
            if len(self.business_id)==0 \
                and self.organisation_unit_number.startswith('0037') \
                    and len(self.organisation_unit_number) > 10:

                business_id = self.organisation_unit_number[4:12]
                if BusinessID.is_valid(business_id):
                    self.business_id = business_id

        details = doc.BuyerPartyDetailsSet
        if len(details) > 0:
            self.name = \
                details[0].BuyerOrganisationNameSet.as_string(delim=' ')
            customer_number = details[0].BuyerPartyIdentifierSet
            if len(customer_number)>0 and customer_number[0].text:
                self.customer_number = customer_number[0].text

            taxcode = details[0].BuyerOrganisationTaxCodeSet
            if len(taxcode) > 0 and taxcode[0].text:
                self.organisation_taxcode = str(taxcode[0].text)
                if len(self.business_id)==0:
                    if BusinessID.is_valid(self.organisation_taxcode):
                        self.business_id = \
                            str(BusinessID(self.organisation_taxcode))

            if len(self.business_id)==0 and self.customer_number:
                if BusinessID.is_valid(self.customer_number):
                    self.business_id = self.customer_number

            address_details = details[0].BuyerPostalAddressDetailsSet
            if len(address_details) > 0:
                postal_address = BuyerPostalAddress(address_details[0])
                self.postal_address = postal_address

        contact_name = doc.BuyerContactPersonNameSet
        if len(contact_name) > 0:
            self.contact_name = contact_name[0].text

        comm_details = doc.BuyerCommunicationDetailsSet
        if len(comm_details) > 0:
            phone = comm_details[0].BuyerPhoneNumberIdentifierSet
            if len(phone) > 0:
                self.contact_phone = phone[0].text
            email = comm_details[0].BuyerEmailaddressIdentifierSet
            if len(email) > 0:
                self.contact_email = email[0].text


class Row(object):

    name = None
    unit_price = None
    quantity = None
    total_taxed = None
    total_untaxed = None
    vat_amount = None
    unit_price_currency = None
    total_taxed_currency = None
    total_untaxed_currency = None
    vat_amount_currency = None
    vat_percent = None
    date = None
    unit_code = None
    freetext = None
    article_identifier = None
    account_dimension_text = None

    def __init__(self, row):
        self.name = row.ArticleNameSet.as_string()

        def get_QuantitySetData(set):
            if len(set) > 0:
                quantity = set[0].text
                try:
                    self.quantity = Decimal(quantity)
                except Exception:
                    pass
                unit_codes = [set[0].attributes.get('quantityunitcode', '').strip()]

                for q in set[1:]:
                    unit_code = ("%s %s"
                                 % (q.text,
                                 q.attributes.get('quantityunitcode', ''))).strip()
                    unit_codes.append(unit_code)
                self.unit_code = '\n'.join(unit_codes)
 
        get_QuantitySetData(row.DeliveredQuantitySet)

        if self.quantity < 1:
            get_QuantitySetData(row.ConfirmedQuantitySet)
        if self.quantity < 1:
            get_QuantitySetData(row.OrderedQuantitySet)

        article_identifier = row.ArticleIdentifierSet
        if len(article_identifier) > 0:
            self.article_identifier = article_identifier[0].text

        unit_price = row.UnitPriceAmountSet
        if len(unit_price) > 0 and unit_price[0]:
            _unit_price = str(unit_price[0].text).strip()
            if len(_unit_price)>0:
                self.unit_price = _Decimal(_unit_price)
                currency = \
                    unit_price[0].attributes.get('amountcurrencyidentifier', '')
                self.unit_price_currency = currency

        total_taxed = row.RowAmountSet
        if len(total_taxed) > 0 and total_taxed[0].text:
            _total_taxed = str(total_taxed[0].text).strip()
            if len(_total_taxed)>0:
                self.total_taxed = _Decimal(_total_taxed)
                currency = \
                    total_taxed[0].attributes.get('amountcurrencyidentifier',
                                                  '')
                self.total_taxed_currency = currency

        total_untaxed = row.RowVatExcludedAmountSet
        if len(total_untaxed) > 0 and total_untaxed[0].text:
            _total_untaxed = str(total_untaxed[0].text).strip()
            if len(_total_untaxed)>0:
                self.total_untaxed = _Decimal(_total_untaxed)
                currency = \
                    total_untaxed[0].attributes.get(
                    'amountcurrencyidentifier', '')
                self.total_untaxed_currency = currency

        vat_amount = row.RowVatAmountSet
        if len(vat_amount) and vat_amount[0].text:
            _vat_amount = str(vat_amount[0].text).strip()
            if len(_vat_amount)>0:
                self.vat_amount = _Decimal(_vat_amount)
                currency = \
                    vat_amount[0].attributes.get('amountcurrencyidentifier', '')
                self.vat_amount_currency = currency

        vat_percent = row.RowVatRatePercentSet
        if len(vat_percent) > 0:
            self.vat_percent = vat_percent[0].text

        account_dimension_text = row.RowAccountDimensionTextSet
        if len(account_dimension_text) > 0:
            self.account_dimension_text = account_dimension_text[0].text

        date_id = row.RowIdentifierDateSet
        delivery_date = row.RowDeliveryDateSet
        if len(date_id) > 0:
            self.date = date_id[0].text
        elif len(delivery_date)>0:
            self.date = delivery_date[0].text

        for element in row.RowFreeTextSet:
            if not self.freetext:
                self.freetext = ''
            self.freetext += '%s\n' % ((element.text or ''), )

    def dict(self):
        return {
            'name': self.name,
            'article_identifier': self.article_identifier,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total_taxed': self.total_taxed,
            'total_untaxed': self.total_untaxed,
            'vat_amount': self.vat_amount,
            'date': self.date,
            'account_dimension_text': self.account_dimension_text}


class FinvoiceWrapper(object):

    version = None
    payee = None
    payer = None
    delivery_party = None
    invoice_recipient = None
    invoice = None
    rows = None
    errors = None
    warnings = None

    def __init__(self, msg=None):
        self.errors = []
        self.warnings = []
        doc = msg.get_payload()
        envelope = msg.get_envelope()
        self.payee = Payee(doc, envelope)
        self.payer = Payer(doc, envelope)
        self.delivery_party = DeliveryParty(doc)
        self.invoice_recipient = InvoiceRecipient(doc)
        self.invoice = Invoice(doc)
        self.rows = self.get_rows(doc)
        self.version = doc.version

        self.errors = doc.get_errors(error_type='ERROR')
        self.warnings = doc.get_errors(error_type='WARNING')

        self.check_finvoice_version(doc)
        self.validate_invoice_totals()

    def check_finvoice_version(self, doc):
        if doc.version != '1.2':
            self.warnings.append(Warning('Finvoice version used is %s.'
                ' Current implementation was written for version 1.2.'))

    def validate_invoice_totals(self):
        if self.invoice.total_taxed:
            total_taxed = sum([row.total_taxed for row in self.rows \
                if row.total_taxed != None])
            if total_taxed != self.invoice.total_taxed:
                description = ('Value of the element'
                    ' InvoiceTotalVatIncludedAmount does not match with the'
                    ' sum of RowAmount elements in the InvoiceRow aggregate.')
                self.errors.append(ValueMismatchError(description))

    def get_rows(self, doc):
        rows = []
        for row in doc.InvoiceRowSet:
            r = Row(row)
            rows.append(r)
        return rows
