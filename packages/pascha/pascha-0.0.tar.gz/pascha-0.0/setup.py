#!/usr/bin/env python

#------------------------------------------------------------------------------#
#   setup.py                                                                   #
#                                                                              #
#   Copyright (c) 2008, Enfold Systems, Inc.                                   #
#   All rights reserved.                                                       #
#                                                                              #
#   Redistribution and use in source and binary forms, with or without         #
#   modification, are permitted provided that the following conditions are     #
#   met:                                                                       #
#                                                                              #
#   - Redistributions of source code must retain the above copyright notice,   #
#     this list of conditions and the following disclaimer.                    #
#                                                                              #
#   - Redistributions in binary form must reproduce the above copyright        #
#     notice, this list of conditions and the following disclaimer in the      #
#     documentation and/or other materials provided with the distribution.     #
#                                                                              #
#   - Neither the name of Enfold Systems, Inc. nor the names of its            #
#     contributors may be used to endorse or promote products derived from     #
#     this software without specific prior written permission.                 #
#                                                                              #
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS    #
#   IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,  #
#   THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR     #
#   PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR           #
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,      #
#   EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,        #
#   PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR         #
#   PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF     #
#   LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING       #
#   NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS         #
#   SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.               #
#------------------------------------------------------------------------------#

# vim: tabstop=4 expandtab shiftwidth=4

from setuptools import setup, find_packages

setup(name             = 'pascha',
      version          = '0.0',
      packages         = find_packages(),
      author           = 'Rajiv Bakulesh Shah',
      author_email     = 'raj@enfoldsystems.com',
      maintainer       = 'Rajiv Bakulesh Shah',
      maintainer_email = 'raj@enfoldsystems.com',
      description      = 'Pascha (Easter) Computation Utility Library',
      long_description = 'Pascha (Easter) Computation Utility Library',
      url              = 'http://pypi.python.org/pypi/pascha/',
      classifiers      = ['Development Status :: 3 - Alpha',
                          'Intended Audience :: Developers',
                          'Intended Audience :: Religion',
                          'License :: OSI Approved :: BSD License',
                          'Operating System :: OS Independent',
                          'Programming Language :: Python',
                          'Topic :: Religion',
                          'Topic :: Software Development :: Libraries',
                          'Topic :: Utilities'],)
