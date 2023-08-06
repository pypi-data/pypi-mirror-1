#!/usr/bin/env python

#------------------------------------------------------------------------------#
#   tests.py                                                                   #
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


import unittest

from datetime import datetime

from pascha.feasts import Feasts
from pascha.traditions import Western, Eastern


class Tests(unittest.TestCase, object):

    def test_western(self):
        answer = datetime(2008, 3, 23)
        f = Feasts(Western)
        f.change_year(2008)
        self.assertEqual(f.feast_to_date('Easter'), answer)
        self.assert_('Easter' in f.date_to_feasts(3, 23))

    def test_eastern(self):
        answer = datetime(2008, 4, 27)
        f = Feasts(Eastern)
        f.change_year(2008)
        self.assertEqual(f.feast_to_date('Pascha'), answer)
        self.assert_('Pascha' in f.date_to_feasts(4, 27))

if __name__ == '__main__':
    unittest.main()
