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
    b = year / 100
    c = year % 100
    d = b / 4
    e = b % 4
    f = (b + 8) / 25
    g = (b - f + 1) / 3
    h = (19 * a + b - d - g + 15) % 30
    i = c / 4
    k = c % 4
    L = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * L) / 451
    month = (h + L - 7 * m + 114) / 31
    day = (h + L - 7 * m + 114) % 31 + 1
    dt = datetime(year, month, day)
    return dt


def eastern(object, year=localtime()[0]):

    """
    For a given year, compute and return the date of Pascha.

    For more information, see:
        http://www.assa.org.au/edm.html#OrthCalculator
    """

    #
    paschal_full_moon = [(4,  5), (3, 25), (4, 13), (4,  2), (3, 22), (4, 10),
                         (3, 30), (4, 18), (4,  7), (3, 27), (4, 15), (4,  4),
                         (3, 24), (4, 12), (4,  1), (3, 21), (4,  9), (3, 29),
                         (4, 17)]

    #
    paschal_full_moon_date_for_year = {(3, 21): 2, (3, 22): 3, (3, 23): 4,
                                       (3, 24): 5, (3, 25): 6, (3, 26): 0,
                                       (3, 27): 1, (3, 28): 2, (3, 29): 3,
                                       (3, 30): 4, (3, 31): 5, (4,  1): 6,
                                       (4,  2): 0, (4,  3): 1, (4,  4): 2,
                                       (4,  5): 3, (4,  6): 4, (4,  7): 5,
                                       (4,  8): 6, (4,  9): 0, (4, 10): 1,
                                       (4, 11): 2, (4, 12): 3, (4, 13): 4,
                                       (4, 14): 5, (4, 15): 6, (4, 16): 0,
                                       (4, 17): 1, (4, 18): 2}

    #
    first_2_digits_of_year = {10: 2, 11: 1, 12: 0, 13: 6, 14: 5, 15: 4, 16: 3,
                              17: 2, 18: 1, 19: 0, 20: 6, 21: 5, 22: 4, 23: 3,
                              24: 2, 25: 1, 26: 0, 27: 6, 28: 5, 29: 4, 30: 3,
                              31: 2, 32: 1, 33: 0}

    #
    last_2_digits_of_year = { 0: 0,  1: 1,  2: 2,  3: 3,  4: 5,  5: 6,  6: 0,
                              7: 1,  8: 3,  9: 4, 10: 5, 11: 6, 12: 1, 13: 2,
                             14: 3, 15: 4, 16: 6, 17: 0, 18: 1, 19: 2, 20: 4,
                             21: 5, 22: 6, 23: 0, 24: 2, 25: 3, 26: 4, 27: 5,
                             28: 0, 29: 1, 30: 2, 31: 3, 32: 5, 33: 6, 34: 0,
                             35: 1, 36: 3, 37: 4, 38: 5, 39: 6, 40: 1, 41: 2,
                             42: 3, 43: 4, 44: 6, 45: 0, 47: 1, 47: 2, 48: 4,
                             49: 5, 50: 6, 51: 0, 52: 2, 53: 3, 54: 4, 55: 5,
                             56: 0, 57: 1, 58: 2, 59: 3, 60: 5, 61: 6, 62: 0,
                             63: 1, 64: 3, 65: 4, 66: 5, 67: 6, 68: 1, 69: 2,
                             70: 3, 71: 4, 72: 6, 73: 0, 74: 1, 75: 2, 76: 4,
                             77: 5, 78: 6, 79: 0, 80: 2, 81: 3, 82: 4, 83: 5,
                             84: 0, 85: 1, 86: 2, 87: 3, 88: 5, 89: 6, 90: 0,
                             91: 1, 92: 3, 93: 4, 94: 5, 95: 6, 96: 1, 97: 2,
                             98: 3, 99: 4}

    #
    following_sunday = { 0: 7,  1: 6,  2: 5,  3: 4,  4: 3,  5: 2,  6: 1,  7: 7,
                         8: 6,  9: 5, 10: 4, 11: 3, 12: 2, 13: 1, 14: 7, 15: 6,
                        16: 5, 17: 4, 18: 3}
    #
    assert year >= 1054 and year <= 3399

    #
    month, day = paschal_full_moon[year % 19]
    dt = datetime(year, month, day)

    #
    total = paschal_full_moon_date_for_year[(month, day)]
    total += first_2_digits_of_year[year / 100]
    total += last_2_digits_of_year[year % 100]
    td = timedelta(following_sunday[total])
    dt += td

    #
    if   (year >= 1583 and year <= 1699): td = timedelta(10)
    elif (year >= 1700 and year <= 1799): td = timedelta(11)
    elif (year >= 1800 and year <= 1899): td = timedelta(12)
    elif (year >= 1900 and year <= 2099): td = timedelta(13)
    elif (year >= 2100 and year <= 2199): td = timedelta(14)
    elif (year >= 2200 and year <= 2299): td = timedelta(15)
    elif (year >= 2300 and year <= 2499): td = timedelta(16)
    elif (year >= 2500 and year <= 2599): td = timedelta(17)
    elif (year >= 2600 and year <= 2699): td = timedelta(18)
    elif (year >= 2700 and year <= 2899): td = timedelta(19)
    elif (year >= 2900 and year <= 2999): td = timedelta(20)
    elif (year >= 3000 and year <= 3099): td = timedelta(21)
    elif (year >= 3100 and year <= 3299): td = timedelta(22)
    elif (year >= 3300 and year <= 3399): td = timedelta(23)
    else:                                 td = timedelta( 0)
    dt += td

    return dt
