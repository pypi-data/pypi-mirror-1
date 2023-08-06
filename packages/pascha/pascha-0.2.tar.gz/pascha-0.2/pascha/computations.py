#!/usr/bin/env python

#------------------------------------------------------------------------------#
#   computations.py                                                            #
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


from datetime import datetime, timedelta
from time import localtime


def western(object, year=localtime()[0]):
    """
    For a given year, compute and return the date of Pascha.

    If this method looks complicated, that's because it is, but it faithfully
    implements the Meeus / Jones / Butcher Gregorian algorithm.

    For more information, see:
        http://en.wikipedia.org/wiki/Computus
    """
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) / 25
    g = (b - f + 1) / 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    L = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * L) / 451
    month, day = divmod(h + L - 7 * m + 114, 31)
    day += 1
    dt = datetime(year, month, day)
    return dt


def eastern(object, year=localtime()[0]):

    """
    For a given year, compute and return the date of Pascha.

    For more information, see:
        http://www.assa.org.au/edm.html#OrthCalculator
    """

    #
    full_moon = [(4,  5), (3, 25), (4, 13), (4,  2), (3, 22), (4, 10), (3, 30),
                 (4, 18), (4,  7), (3, 27), (4, 15), (4,  4), (3, 24), (4, 12),
                 (4,  1), (3, 21), (4,  9), (3, 29), (4, 17)]

    #
    short_year = [0, 1, 2, 3, 5, 6, 0, 1, 3, 4, 5, 6, 1, 2, 3, 4, 6, 0, 1, 2, 4,
                  5, 6, 0, 2, 3, 4, 5]

    #
    assert year >= 1054 and year <= 3399

    #
    month, day = full_moon[year % 19]
    dt = datetime(year, month, day)

    #
    x = (dt - datetime(year, 3, 19)).days % 7
    x += (5 - year / 100) % 7
    x += short_year[year % 100 % 28]
    num_days_to_add = 7 - x % 7

    #
    if year >= 1583:
        l = [x for x in range(1700, 3400, 100) if x % 400 != 0 and x <= year]
        num_days_to_add += 10 + len(l)

    td = timedelta(num_days_to_add)
    dt += td
    return dt
