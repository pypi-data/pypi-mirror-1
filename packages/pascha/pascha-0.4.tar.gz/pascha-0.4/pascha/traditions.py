#!/usr/bin/env python

#------------------------------------------------------------------------------#
#   traditions.py                                                              #
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


from datetime import timedelta

from pascha.computus import western, eastern


class Western(object):

    """
    """

    #
    compute_pascha = western

    # This dictionary contains key, value pairs where a key is a feast name and
    # its corresponding value is the feast's offset from Pascha in days
    # (negative for before Pascha and positive for after Pascha).
    offset = {}

    def __init__(self):
        """
        Initialize a Western object.

        The only necessary initialization is defining a dictionary, self.offset.
        Its keys represent the various moveable feasts, and its values represent
        the feasts' respective offsets (in days) from Easter.

        In other words, self.offset['Good Friday'] equals timedelta(-2), since
        Good Friday comes two days before Easter Sunday.

        For more information, see:
            http://en.wikipedia.org/wiki/Moveable_feast
        """
        self.offset['Ash Wednesday']        = timedelta(-46)
        self.offset['Palm Sunday']          = timedelta( -7)
        self.offset['Good Friday']          = timedelta( -2)
        self.offset['Easter']               = timedelta(  0)
        self.offset['The Octave of Easter'] = timedelta(  7)
        self.offset['Ascension Day']        = timedelta( 39)
        self.offset['Pentecost']            = timedelta( 49)
        self.offset['Trinity Sunday']       = timedelta( 56)
        self.offset['Corpus Christi']       = timedelta( 60)


class Eastern(object):

    """
    """

    #
    compute_pascha = eastern

    # This dictionary contains key, value pairs where a key is a feast name and
    # its corresponding value is the feast's offset from Pascha in days
    # (negative for before Pascha and positive for after Pascha).
    offset = {}

    def __init__(self):

        """
        Initialize an Eastern object.

        The only necessary initialization is defining a dictionary, self.offset.
        Its keys represent the various moveable feasts, and its values represent
        the feasts' respective offsets (in days) from Pascha (Easter).

        In other words, self.offset['Great and Holy Friday'] equals
        timedelta(-2), since Great and Holy Friday (Good Friday) comes two days
        before Pascha (Easter Sunday).

        For more information, see:
            http://en.wikipedia.org/wiki/Paschal_Cycle
        """

        self.offset['Pascha']                                      = timedelta(  0)

        # Pre-Lent Feasts:
        self.offset['Zacchaeus Sunday']                            = timedelta(-77)
        self.offset['Sunday of the Canaanite']                     = timedelta(-77)
        self.offset['The Publican and the Pharisee']               = timedelta(-70)
        self.offset['The Prodigal Son']                            = timedelta(-63)
        self.offset['The Last Judgment']                           = timedelta(-56)
        self.offset['Meat-Fare Sunday']                            = timedelta(-56)
        self.offset['Sunday of Forgiveness']                       = timedelta(-49)
        self.offset['Cheese-Fare Sunday']                          = timedelta(-49)

        # Great Lent Feasts:
        self.offset['Clean Monday']                                = timedelta(-48)
        self.offset['Theodore Saturday']                           = timedelta(-43)
        self.offset['Triumph of Orthodoxy']                        = timedelta(-42)
        self.offset['Memorial Saturday 1']                         = timedelta(-36)
        self.offset['Memorial Saturday 2']                         = timedelta(-29)
        self.offset['Memorial Saturday 3']                         = timedelta(-22)
        self.offset['Saint Gregory Palamas']                       = timedelta(-35)
        self.offset['Adoration of the Cross']                      = timedelta(-28)
        self.offset['Saint John of the Ladder']                    = timedelta(-21)
        self.offset['Saturday of the Akathist']                    = timedelta(-15)
        self.offset['Saint Mary of Egypt']                         = timedelta(-14)

        # Great and Holy Week Feasts:
        self.offset['Lazarus Saturday']                            = timedelta( -8)
        self.offset['Palm Sunday']                                 = timedelta( -7)
        self.offset['Great and Holy Monday']                       = timedelta( -6)
        self.offset['Great and Holy Tuesday']                      = timedelta( -5)
        self.offset['Great and Holy Wednesday']                    = timedelta( -4)
        self.offset['Great and Holy Thursday']                     = timedelta( -3)
        self.offset['Great and Holy Friday']                       = timedelta( -2)
        self.offset['Great and Holy Saturday']                     = timedelta( -1)

        # Great and Holy Feasts:
        self.offset['The Resurrection of Jesus Christ']            = timedelta(  0)
        self.offset['Agape Vespers']                               = timedelta(  0)

        # Pentecostarion Feasts:
        self.offset['Bright Week']                                 = timedelta(  0)
        self.offset['Thomas Sunday']                               = timedelta(  7)
        self.offset['Radonitsa']                                   = timedelta(  9)
        self.offset['The Holy Myrrhbearers']                       = timedelta( 14)
        self.offset['The Paralytic']                               = timedelta( 21)
        self.offset['The Samaritan Woman']                         = timedelta( 28)
        self.offset['The Blind Man']                               = timedelta( 35)
        self.offset['The Ascension of Jesus Christ']               = timedelta( 39)
        self.offset['The Fathers of the First Ecumenical Council'] = timedelta( 42)
        self.offset['Pentecost']                                   = timedelta( 49)
        self.offset['All Saints']                                  = timedelta( 56)
