#!/usr/bin/env python

#------------------------------------------------------------------------------#
#   feasts.py                                                                  #
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


from datetime import datetime

from pascha.traditions import Western


class Feasts(object):

    """
    This class computes the dates of all of the moveable feasts for a given
    Gregorian year.

    To use this class, study the following example commands and output:

    >>> from pascha.feasts import Feasts
    >>> from pascha.traditions import Western
    >>> f = Feasts(Western)
    >>> f.change_year(2008)
    >>> f.feast_to_date('Pascha')
    >>> f.date_to_feasts(4, 27)
    """

    #
    tradition = Western()

    #
    year = datetime.now().year

    # This dictionary contains key, value pairs where a key is a date and its
    # corresponding value is a list of all of the feasts that fall on that date.
    date = {}

    # This dictionary contains key, value pairs where a key is a feast name and
    # its corresponding value is the date on which that feast falls.
    feasts = {}

    def __init__(self, Tradition=Western, year=datetime.now().year):
        """Initialize a Feasts object."""
        self.tradition = Tradition()
        self.change_year(year)

    def change_year(self, year):
        """Given a year, compute the dates of all of its moveable feasts."""
        self.year = year
        self.date = {}
        self.feasts = {}
        pascha = self.tradition.compute_pascha(year)
        for feast in self.tradition.offset.keys():
            date = pascha + self.tradition.offset[feast]
            self.date[feast] = date
            try:
                self.feasts[date].append(feast)
            except KeyError:
                self.feasts[date] = [feast]

    def feast_to_date(self, feast):
        """Given a feast's name, return the date that it falls on."""
        return self.date[feast]

    def date_to_feasts(self, month, day):
        """Given a date, return a list of all of the feasts that fall on it."""
        dt = datetime(self.year, month, day)
        try:
            return self.feasts[dt]
        except KeyError:
            # Oops, no feast falls on the given date.  Return an empty list.
            return []


def main():
    f = Feasts()

if __name__ == '__main__':
    main()
