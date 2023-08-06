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
        f = Feasts(Western)
        answers = [datetime(1987, 4, 19), datetime(1988, 4,  3),
                   datetime(1989, 3, 26), datetime(1990, 4, 15),
                   datetime(1991, 3, 31), datetime(1992, 4, 19),
                   datetime(1993, 4, 11), datetime(1994, 4,  3),
                   datetime(1995, 4, 16), datetime(1996, 4,  7),
                   datetime(1997, 3, 30), datetime(1998, 4, 12),
                   datetime(1999, 4,  4), datetime(2000, 4, 23),
                   datetime(2001, 4, 15), datetime(2002, 3, 31),
                   datetime(2003, 4, 20), datetime(2004, 4, 11),
                   datetime(2005, 3, 27), datetime(2006, 4, 16),
                   datetime(2007, 4,  8), datetime(2008, 3, 23),
                   datetime(2009, 4, 12), datetime(2010, 4,  4),
                   datetime(2011, 4, 24), datetime(2012, 4,  8),
                   datetime(2013, 3, 31), datetime(2014, 4, 20),
                   datetime(2015, 4,  5), datetime(2016, 3, 27),
                   datetime(2017, 4, 16), datetime(2018, 4,  1),
                   datetime(2019, 4, 21), datetime(2020, 4, 12),
                   datetime(2021, 4,  4), datetime(2022, 4, 17)]
        for answer in answers:
            f.change_year(answer.year)
            self.assertEqual(f.feast_to_date('Easter'), answer)

    def test_eastern(self):
        f = Feasts(Eastern)
        answers = [datetime(1987, 4, 19), datetime(1988, 4, 10),
                   datetime(1989, 4, 30), datetime(1990, 4, 15),
                   datetime(1991, 4,  7), datetime(1992, 4, 26),
                   datetime(1993, 4, 18), datetime(1994, 5,  1),
                   datetime(1995, 4, 23), datetime(1996, 4, 14),
                   datetime(1997, 4, 27), datetime(1998, 4, 19),
                   datetime(1999, 4, 11), datetime(2000, 4, 30),
                   datetime(2001, 4, 15), datetime(2002, 5,  5),
                   datetime(2003, 4, 27), datetime(2004, 4, 11),
                   datetime(2005, 5,  1), datetime(2006, 4, 23),
                   datetime(2007, 4,  8), datetime(2008, 4, 27),
                   datetime(2009, 4, 19), datetime(2010, 4,  4),
                   datetime(2011, 4, 24), datetime(2012, 4, 15),
                   datetime(2013, 5,  5), datetime(2014, 4, 20),
                   datetime(2015, 4, 12), datetime(2016, 5,  1),
                   datetime(2017, 4, 16), datetime(2018, 4,  8),
                   datetime(2019, 4, 28), datetime(2020, 4, 19),
                   datetime(2021, 5,  2), datetime(2022, 4, 24)]
        for answer in answers:
            f.change_year(answer.year)
            self.assertEqual(f.feast_to_date('Pascha'), answer)

if __name__ == '__main__':
    unittest.main()
