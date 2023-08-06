#!/usr/bin/env python
##############################################################################
# Copyright 2008, Gerhard Weis
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  * Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#  * Neither the name of the authors nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT
##############################################################################
import os
from setuptools import setup
from setuptools import find_packages
# for setuptools see: http://peak.telecommunity.com/DevCenter/setuptools

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name = 'rsl.mime',
      version = '0.2.1',
      package_dir={'': 'src'},
      packages = find_packages('src', exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
      
      namespace_packages = ['rsl'],
      
      # dependencies:
      install_requires = ['rsl >= 0.2.0',
                          'rsl.xsd >= 0.2.0',
                          'rsl.wsdl1 >= 0.2.1',
                          'zope.interface',
                          'lxml >= 2.0',
                          'setuptools'],
      
      # PyPI metadata
      author='Gerhard Weis',
      author_email='gerhard.weis@proclos.com',
      description='Remote Service Library mime encoding module',
      license = 'BSD-like',
      #keywords = '',
      url='http://sourceforge.net/projects/rslib/',

      long_description=read('README.txt') +
                       read('CHANGES.txt'),
      
      #download_url='',
      classifiers = ['Development Status :: 3 - Alpha',
                     'Environment :: Web Environment',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: BSD License',
                     'Operating System :: OS Independent',
                     'Programming Language :: Python',
                     'Topic :: Internet',
                     'Topic :: Software Development :: Libraries :: Python Modules',
                     'Topic :: System :: Networking',
                     ],
      data_files = [],
      entry_points = {'rsl.register': ['method = rsl.mime.factories:register'],
                      'rsl.wsdl1.binding.operation.input' : [ 'http://schemas.xmlsoap.org/wsdl/mime/ = rsl.mime.wsdl1:mimeparaminfofactory' ],
                      'rsl.wsdl1.binding.operation.output' : [ 'http://schemas.xmlsoap.org/wsdl/mime/ = rsl.mime.wsdl1:mimeparaminfofactory' ] }
     )
