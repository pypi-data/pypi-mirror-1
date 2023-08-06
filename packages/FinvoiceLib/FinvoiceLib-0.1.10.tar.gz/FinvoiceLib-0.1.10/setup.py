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

from setuptools import setup, find_packages

version = '0.1.10'


setup(name='FinvoiceLib',
      author='Norfello Oy',
      author_email='opensource@norfello.com',
      version=version,
      description="A library for reading Finvoice XML files",
      long_description="""
Finvoice is one of most commonly used XML dialects used for electronic
invoicing in Finland.

One of the major drawbacks of this format has been the lack of commonly
available libraries for reading this format. This is exactly why Norfello
developed an open source library for reading the format. With this library you
can easily incorporate the receiving of Finvoice based messages to your
software.

FinvoiceLib consists of two main components: Reader and FinvoiceWrapper.
The Reader component is the heart of the library as it encapsulates the full
finvoice 1.2 message to a class based structure. This class structure can then
be used access every single element found in the message. The second component,
FinvoiceWrapper, wraps the most commonly used elements to a convinient helper
class, that allows to access any of available elements with only a one single
line of code!
      """,
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'Intended Audience :: Financial and Insurance Industry',
                   'License :: OSI Approved :: BSD License',
                   'Programming Language :: Python',
                   'Topic :: Office/Business', ],
      keywords='finvoice norfello postita.fi',
      url='http://en.norfello.com/',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
      'lxml',
      'business_tools>=0.2.12'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
