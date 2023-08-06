##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Utility helpers

$Id: utils.py 40747 2005-12-12 18:55:06Z benji_york $
"""

from email.Charset import Charset

def decode(s, charset_name):
    "given a string and a IANA character set name, decode string to unicode"
    codec = Charset(charset_name).input_codec
    if codec is None:
        return unicode(s)
    else:
        return unicode(s, codec)
