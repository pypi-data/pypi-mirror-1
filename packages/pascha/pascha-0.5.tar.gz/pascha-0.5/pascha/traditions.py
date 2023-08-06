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
    computus = western

    # This dictionary contains key, value pairs where a key is a moveable
    # feast's name and its corresponding value is the feast's offset from Pascha
    # in days (negative for before Pascha and positive for after Pascha).
    #
    # In other words, offset['Good Friday'] equals timedelta(-2) since Good
    # Friday comes two days before Easter Sunday.
    #
    # For more information, see:
    #   http://en.wikipedia.org/wiki/Moveable_feast
    offset = {
        'Ash Wednesday'        : timedelta(-46),
        'Palm Sunday'          : timedelta( -7),
        'Good Friday'          : timedelta( -2),
        'Easter'               : timedelta(  0),
        'The Octave of Easter' : timedelta(  7),
        'Ascension Day'        : timedelta( 39),
        'Pentecost'            : timedelta( 49),
        'Trinity Sunday'       : timedelta( 56),
        'Corpus Christi'       : timedelta( 60),
        }


class Eastern(object):

    """
    """

    #
    computus = eastern

    # This dictionary contains key, value pairs where a key is a moveable
    # feast's name and its corresponding value is the feast's offset from Pascha
    # in days (negative for before Pascha and positive for after Pascha).
    #
    # In other words, offset['Great and Holy Friday'] equals timedelta(-2) since
    # Great and Holy Friday (Good Friday) comes two days before Pascha (Easter
    # Sunday).
    #
    # For more information, see:
    #   http://en.wikipedia.org/wiki/Paschal_Cycle
    offset = {
        # Pre-Lent Feasts:
        'Zacchaeus Sunday'                            : timedelta(-77),
        'Sunday of the Canaanite'                     : timedelta(-77),
        'The Publican and the Pharisee'               : timedelta(-70),
        'The Prodigal Son'                            : timedelta(-63),
        'The Last Judgment'                           : timedelta(-56),
        'Meat-Fare Sunday'                            : timedelta(-56),
        'Sunday of Forgiveness'                       : timedelta(-49),
        'Cheese-Fare Sunday'                          : timedelta(-49),
        # Great Lent Feasts:
        'Clean Monday'                                : timedelta(-48),
        'Theodore Saturday'                           : timedelta(-43),
        'Triumph of Orthodoxy'                        : timedelta(-42),
        'Memorial Saturday 1'                         : timedelta(-36),
        'Memorial Saturday 2'                         : timedelta(-29),
        'Memorial Saturday 3'                         : timedelta(-22),
        'Saint Gregory Palamas'                       : timedelta(-35),
        'Adoration of the Cross'                      : timedelta(-28),
        'Saint John of the Ladder'                    : timedelta(-21),
        'Saturday of the Akathist'                    : timedelta(-15),
        'Saint Mary of Egypt'                         : timedelta(-14),
        # Great and Holy Week Feasts:
        'Lazarus Saturday'                            : timedelta( -8),
        'Palm Sunday'                                 : timedelta( -7),
        'Great and Holy Monday'                       : timedelta( -6),
        'Great and Holy Tuesday'                      : timedelta( -5),
        'Great and Holy Wednesday'                    : timedelta( -4),
        'Great and Holy Thursday'                     : timedelta( -3),
        'Great and Holy Friday'                       : timedelta( -2),
        'Great and Holy Saturday'                     : timedelta( -1),
        # Great and Holy Feasts:
        'Pascha'                                      : timedelta(  0),
        'The Resurrection of Jesus Christ'            : timedelta(  0),
        'Agape Vespers'                               : timedelta(  0),
        # Pentecostarion Feasts:
        'Bright Week'                                 : timedelta(  0),
        'Thomas Sunday'                               : timedelta(  7),
        'Radonitsa'                                   : timedelta(  9),
        'The Holy Myrrhbearers'                       : timedelta( 14),
        'The Paralytic'                               : timedelta( 21),
        'The Samaritan Woman'                         : timedelta( 28),
        'The Blind Man'                               : timedelta( 35),
        'The Ascension of Jesus Christ'               : timedelta( 39),
        'The Fathers of the First Ecumenical Council' : timedelta( 42),
        'Pentecost'                                   : timedelta( 49),
        'All Saints'                                  : timedelta( 56),
        }
