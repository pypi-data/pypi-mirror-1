##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
"""
$Id: header.py 92074 2008-10-12 12:26:46Z ccomb $
"""
__docformat__ = "reStructuredText"

from urllib import urlencode

import zope.interface

from z3c.table import interfaces


class ColumnHeader(object):
    """ColumnHeader renderer provider"""

    zope.interface.implements(interfaces.IColumnHeader)

    _request_args = []

    def __init__(self, context, request, table, column):
        self.__parent__ = context
        self.context = context
        self.request = request
        self.table = table
        self.column = column

    def update(self):
        """Override this method in subclasses if required"""
        pass

    def render(self):
        """Override this method in subclasses"""
        return self.column.header

    def getQueryStringArgs(self):
        """
        Collect additional terms from the request and include in sorting column
        headers

        Perhaps this should be in separate interface only for sorting headers?

        """
        args = {}
        for key in self._request_args:
            value = self.request.get(key, None)
            if value:
                args.update({key: value})
        return args


class SortingColumnHeader(ColumnHeader):
    """Sorting column header."""

    def render(self):
        table = self.table
        prefix = table.prefix
        colID = self.column.id

        # this may return a string 'id-name-idx' if coming from request,
        # otherwise in Table class it is intialised as a integer string
        currentSortID = table.getSortOn()
        try:
            currentSortID = int(currentSortID)
        except ValueError:
            currentSortID = currentSortID.split('-')[2]

        currentSortOrder = table.getSortOrder()

        sortID = colID.split('-')[2]

        sortOrder = table.sortOrder
        if int(sortID) == int(currentSortID):
            # ordering the same column so we want to reverse the order
            if currentSortOrder in table.reverseSortOrderNames:
                sortOrder = 'ascending'
            elif currentSortOrder == 'ascending':
                sortOrder = table.reverseSortOrderNames[0]

        args = self.getQueryStringArgs()
        args.update({'%s-sortOn' % prefix: colID,
                     '%s-sortOrder' % prefix: sortOrder})
        queryString = '?%s' % (urlencode(args))

        return '<a href="%s" title="Sort">%s</a>' % (queryString, 
                                                self.column.header)

