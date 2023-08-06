##############################################################################
#
# Copyright (c) 2005-2009 Zope Corporation and Contributors.
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
"""Query interfaces

$Id: interfaces.py 103475 2009-09-01 22:07:08Z nadako $
"""

from zope.interface import Interface

class IQuery(Interface):

    def searchResults(query):
        """Query indexes.

        Argument is a query composed of terms.
        """
