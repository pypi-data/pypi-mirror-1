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


import time

import datetime
from business_tools import BBAN
from business_tools import IBAN
from business_tools import BusinessID
from business_tools import ReferenceNumber
from decimal import Decimal
from finvoicelib.error import ElementMissingError
from finvoicelib.error import InvalidValue
from finvoicelib.error import UnknownAttributeWarning
from finvoicelib.error import UnknownElementWarning
from finvoicelib.mapping import Map


class Element(object):

    required = False
    tag = None
    tag_ns = None
    children = None
    text = None
    node = None
    supported_elements = []
    aggregate = []
    errors = None
    attributes = None

    def __repr__(self):
        return "<Element: %s>" % self.tag

    def __init__(self, tag=None):
        if tag:
            self.tag = tag
        if not self.tag_ns:
            self.tag_ns = ''
        self.errors = []
        self.children = []
        self.text = ''
        self.node = None
        self.set_children()
        self.set_attributes()
        self._set_supported_elements()

    def set_aggregate(self):
        self.aggregate = []

    def set_children(self):
        self.children = []
        for node in self.aggregate:
            self.children.append(Map(node))

    def set_attributes(self):
        self.attributes = {}

    def _set_supported_elements(self):
        self.supported_elements = []
        for child in self.children:
            self.supported_elements.append(child.tag)

    def get_children_by_name(self, name):
        for child in self.children:
            if child.tag == name:
                return child.collection
        return None

    def has_mapping_for(self, tag):
        if self.tag_ns:
            tag = tag.replace(self.tag_ns, '')
        if tag in self.supported_elements:
            return True
        return False

    def _validate(self):
        # Implemented by subclass
        return True

    def add_node(self, node):
        tag = node.tag
        if self.tag_ns:
            tag = tag.replace(self.tag_ns, '')
        if tag not in self.supported_elements:
            self.errors.append(UnknownElementWarning(node))
            return

        t = [(i, e.tag) for i, e in enumerate(self.children) if e.tag == tag]
        if len(t) < 1:
            return

        t = t[0]
        i = t[0]
        e = self.children[i]
        obj = e.cls(node.tag)
        obj.build(node)
        self.children[i].add(obj)

    def __getattr__(self, attr):
        if attr in self.attributes:
            return self.attributes[attr]

        if not attr.endswith('Set'):
            raise AttributeError(attr)

        attr = attr[:-3]

        t = [(i, e.tag) for i, e in \
            enumerate(self.__dict__['children']) if e.tag == attr]

        if len(t) < 1:
            raise AttributeError(attr)
        t = t[0]

        return self.__dict__['children'][t[0]]

    def build_children(self, tree):
        for node in tree.iterchildren():
            tag = node.tag
            if tag == self.tag:
                continue
            if self.has_mapping_for(tag):
                self.add_node(node)
            else:
                self.errors.append(UnknownElementWarning(node))

    def build(self, tree):
        for attr in tree.attrib:
            normalized_attr = attr.lower()
            if normalized_attr in self.attributes:
                self.attributes[normalized_attr] = tree.attrib[attr]
            else:
                self.errors.append(UnknownAttributeWarning(tree, attr))

        self.set_node(tree)
        self.set_text(tree.text)
        self.build_children(tree)
        self.validate()

    def get_errors(self, error_type):
        if error_type not in ('WARNING', 'ERROR'):
            raise Exception('Unknown error type!')

        my_errors = [err for err in self.errors \
                        if err.error_type == error_type]

        my_errors += self.get_child_errors(error_type)
        return my_errors

    def get_child_errors(self, error_type):
        errors = []
        for map in self.children:
            for child in map:
                errors += child.get_errors(error_type)
        return errors

    def validate(self):
        counters = dict([(key, 0) for key in self.supported_elements])
        for mapper in self.children:
            for e in mapper.collection:
                counters[e.tag] += 1

        for element in self.aggregate:
            if element.required and counters[element.tag] < 1:
                self.errors.append(ElementMissingError(element))

    def set_text(self, value):
        self.text = value

    def set_node(self, value):
        self.node = value


class DateElement(Element):

    text = None

    def set_attributes(self):
        self.attributes = {'format': 'CCYYMMDD'}

    def set_text(self, value):
        format = self.attributes['format']
        if len(format) < 1:
            self.errors.append(InvalidValue(self.node, value))
            self.format = 'CCYYMMDD'

        format = format.replace('CCYY', r'%Y')
        format = format.replace('YYYY', r'%Y')
        format = format.replace('CCCC', r'%Y') # hack
        format = format.replace('MM', r'%m')
        format = format.replace('DD', r'%d')

        try:
            self.text = datetime.date(*time.strptime(value, format)[0:3])
        except (ValueError, TypeError), e:
            self.errors.append(InvalidValue(self.node, value))
            self.text = None


class BusinessIdElement(Element):

    def set_text(self, value):
        self.text = None
        try:
            self.text = BusinessID(value)
        except ValueError, e:
            self.errors.append(InvalidValue(self.node, value))


class ReferenceNumberElement(Element):

    def set_text(self, value):
        self.text = None
        try:
            if ReferenceNumber.is_valid(value):
                self.text = ReferenceNumber(value)
        except ValueError, e:
            self.errors.append(InvalidValue(self.node, value))


class DecimalElement(Element):

    def set_text(self, value):
        try:
            if isinstance(value, basestring):
                value = value.replace(',', '.')
            self.text = Decimal(value)
        except ValueError, e:
            self.errors.append(InvalidValue(self.node, value))


class CurrencyElement(Element):

    def set_attributes(self):
        self.attributes = {'amountcurrencyidentifier': ''}


class AccountElement(Element):

    def set_text(self, value):
        if not value:
            self.errors.append(InvalidValue(self.node, value))
            return

        if len(value)<1:
            self.errors.append(InvalidValue(self.node, value))
            return

        if ord(value[0])>60:
            try:
                self.text = IBAN(value)
            except ValueError, e:
                self.errors.append(InvalidValue(self.node, value))
        else:
            try:
                self.text = BBAN(value)
            except ValueError, e:
                self.errors.append(InvalidValue(self.node, value))
