##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Sample Component

$Id: sample.py 1946 2007-05-04 16:11:29Z hazmat $
"""
from ore.dtmlview import DTMLViewFile

class Sample(object):
    index = DTMLViewFile('test.dtml')
    scripted = DTMLViewFile('test.js')

    request = None
    context = None
    
#print Sample().index()
#print Sample().scripted()
