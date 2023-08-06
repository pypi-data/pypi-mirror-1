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


import sys

from finvoicelib.reader import Reader
from finvoicelib.wrapper import FinvoiceWrapper


def finvoice_info(filename):
    print 'Reading: %s' % filename

    try:
        reader = Reader(filename)
    except Exception, e:
        print 'Fatal error. Cannot continue'
        return
    msg = reader.messages[0]

    payload = msg.get_payload()

    if not payload:
        print 'No payload!'

    payload.validate()
    print ' Document '.center(71, '=')
    print 'Version: %s' % payload.version
    print
    print 'Errors: %s' % len(payload.get_errors('ERROR'))
    print 'Warnings: %s' % len(payload.get_errors(error_type='WARNING'))
    print

    #print ' Errors '.center(71, '-')
    #for error in payload.get_errors('ERROR'):
    #    print error.get_message()
    #print
    #print ' Warnings '.center(71, '-')
    #for error in payload.get_errors(error_type='WARNING'):
    #    print error.get_message()

    soap = msg.get_envelope()
    if soap:
        print
        print ' SOAP ENVELOPE '.center(71, '=')
        print
        print 'Sender ID: %s (%s)' % (soap.seller_id,
                                      soap.seller_intermediator_id)
        print 'Receiver ID: %s (%s)' % (soap.buyer_id,
                                        soap.buyer_intermediator_id)


    f = FinvoiceWrapper(msg)
    print
    print u' Seller '.center(71, '=')
    payee = f.payee
    print u'Name:\t%s' % (payee.name, )
    print u'Business ID:\t%s' % (payee.business_id, )
    print
    if len(payee.business_id) < 1:
        print 'Invalid payer business id!'
        sys.exit(1)

    print u' Buyer '.center(71, '=')
    payer = f.payer
    print u'Name:\t%s' % (payer.name, )
    print u'Business ID:\t%s' % (payer.business_id, )
    print
    print u'Street:\t%s' % (payer.postal_address.street_name, )
    print u'Town:\t%s' % (payer.postal_address.city, )
    print u'Postal code:\t%s' % (payer.postal_address.postal_code, )
    print u'Country:\t%s' % (payer.postal_address.country, )

    if len(payer.business_id) < 1:
        print 'Invalid payer business id!'
        sys.exit(1)

    print u' Invoice '.center(71, '=')
    invoice = f.invoice
    print u'Type: %s (%s)' % (invoice.typecode, invoice.type_text)
    print u'Date: %s' % invoice.date
    print u'Due date: %s' % invoice.due_date
    print u'Reference: %s' % invoice.reference
    print
    print u'Total (VAT 0%%): %s %s' % (invoice.total_untaxed,
                                       invoice.total_untaxed_currency)
    print u'Vat: %s %s' % (invoice.vat_amount, invoice.vat_amount_currency)
    print u'Total: %s %s' % (invoice.total_taxed, invoice.total_taxed_currency)
    print
    print u' Rows '.center(71, '=')

    print u'Date       Product         Qty. Unit price Vat        Total'
    print '-' * 71
    for row in f.rows:
        print (u'%(date)-10s %(name)-15s %(quantity)-04s %(unit_price)-10s'
               u' %(vat_amount)-10s %(total_taxed)-5s' % row.dict())

        print '-' * 71


def main():
    if len(sys.argv) < 2:
        return
    filename = sys.argv[1]
    print 'Using file: %s' % filename
    finvoice_info(filename)


if __name__ == '__main__':
    main()
