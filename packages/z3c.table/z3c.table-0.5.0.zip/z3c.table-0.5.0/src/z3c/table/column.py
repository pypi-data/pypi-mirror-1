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
$Id:$
"""
__docformat__ = "reStructuredText"

import zope.interface
import zope.location
import zope.i18nmessageid
from zope.dublincore.interfaces import IZopeDublinCore
from zope.security.interfaces import Unauthorized
from zope.traversing import api
from zope.traversing.browser import absoluteURL

from z3c.table import interfaces

_ = zope.i18nmessageid.MessageFactory('z3c')


def addColumn(self, class_, name, cellRenderer=None, headCellRenderer=None,
    colspan= None, weight=None, header=None, cssClasses=None, **kws):
    if not interfaces.IColumn.implementedBy(class_):
        raise ValueError('class_ %s must implement IColumn.' % class_)
    column = class_(self.context, self.request, self)
    column.__parent__ = self
    column.__name__ = name
    if cellRenderer is not None:
        # overload method
        column.renderCell = cellRenderer
    if headCellRenderer is not None:
        # overload method
        column.renderHeadCell = headCellRenderer
    if colspan is not None:
        column.colspan = colspan
    if weight is not None:
        column.weight = weight
    if header is not None:
        column.header = header
    if cssClasses is not None:
        column.cssClasses = cssClasses
    for name, value in kws.items():
        setattr(column, name, value)
    return column


def safeGetAttr(obj, attr, default):
    try:
        return getattr(obj, attr, default)
    except Unauthorized:
        return default



class Column(zope.location.Location):
    """Column provider."""

    zope.interface.implements(interfaces.IColumn)

    # variables will be set by table
    id = None

    # customize this part if needed
    colspan = 0
    weight = 0
    header = u''
    cssClasses = {}

    def __init__(self, context, request, table):
        self.__parent__ = context
        self.context = context
        self.request = request
        self.table = table

    def update(self):
        pass

    def getColspan(self, item):
        """Returns the colspan value."""
        return self.colspan

    def getSortKey(self, item):
        """Returns the sort key used for column sorting."""
        return self.renderCell(item)

    def renderHeadCell(self):
        """Header cell content."""
        header = zope.component.queryMultiAdapter((self.context,
            self.request, self.table, self), interfaces.IColumnHeader)
        if header:
            header.update()
            return header.render()
        return self.header

    def renderCell(self, item):
        """Cell content."""
        raise NotImplementedError('Subclass must implement renderCell')

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.__name__)


class NoneCell(Column):
    """None cell is used for mark a previous colspan."""

    zope.interface.implements(interfaces.INoneCell)

    def getColspan(self, item):
        return 0

    def renderHeadCell(self):
        return u''

    def renderCell(self, item):
        return u''


# predefined columns
class NameColumn(Column):
    """Name column."""

    header = _('Name')

    def renderCell(self, item):
        return api.getName(item)


class RadioColumn(Column):
    """Radio column."""

    header = _('X')
    selectedItem = None

    def getSortKey(self, item):
        return api.getName(item)

    def getItemKey(self, item):
        return '%s-selectedItem' % self.id

    def getItemValue(self, item):
        return api.getName(item)

    def update(self):
        items = [item for item in self.table.values
                 if self.getItemValue(item) in self.request.get(
                     self.getItemKey(item), [])]
        if len(items):
            self.selectedItem = items.pop()
            self.table.selectedItems = [self.selectedItem]

    def renderCell(self, item):
        selected = u''
        if item == self.selectedItem:
            selected='checked="checked"'
        return u'<input type="radio" class="%s" name="%s" value="%s" %s />' %(
            'radio-widget', self.getItemKey(item), self.getItemValue(item),
            selected)


class CheckBoxColumn(Column):
    """Checkbox column."""

    header = _('X')
    weight = 10
    selectedItems = []

    def getSortKey(self, item):
        return api.getName(item)

    def getItemKey(self, item):
        return '%s-selectedItems' % self.id

    def getItemValue(self, item):
        return api.getName(item)

    def update(self):
        self.selectedItems = [item for item in self.table.values
                              if self.getItemValue(item)
                              in self.request.get(
                                self.getItemKey(item), [])]
        self.table.selectedItems = self.selectedItems

    def renderCell(self, item):
        selected = u''
        if item in self.selectedItems:
            selected='checked="checked"'
        return u'<input type="checkbox" class="%s" name="%s" value="%s" %s />' \
            %('checkbox-widget', self.getItemKey(item), self.getItemValue(item), 
            selected)


class GetAttrColumn(Column):
    """Get attribute column."""

    attrName = None
    defaultValue = u''

    def getValue(self, obj):
        if obj is not None and self.attrName is not None:
            return safeGetAttr(obj, self.attrName, self.defaultValue)
        return self.defaultValue

    def renderCell(self, item):
        return self.getValue(item)


class FormatterColumn(Column):
    """Formatter column."""

    formatterCategory = u'dateTime'
    formatterLength = u'medium'
    formatterName = None
    formatterCalendar = u'gregorian'

    def getFormatter(self):
        return self.request.locale.dates.getFormatter(
            self.formatterCategory, self.formatterLength, self.formatterName,
            self.formatterCalendar)


class CreatedColumn(FormatterColumn, GetAttrColumn):
    """Created date column."""

    header = _('Created')
    weight = 100

    formatterCategory = u'dateTime'
    formatterLength = u'short'
    attrName = 'created'

    def renderCell(self, item):
        formatter = self.getFormatter()
        dc = IZopeDublinCore(item, None)
        value = self.getValue(dc)
        if value:
            value = formatter.format(value)
        return value


class ModifiedColumn(FormatterColumn, GetAttrColumn):
    """Created date column."""

    header = _('Modified')
    weight = 110

    formatterCategory = u'dateTime'
    formatterLength = u'short'
    attrName = 'modified'

    def renderCell(self, item):
        formatter = self.getFormatter()
        dc = IZopeDublinCore(item, None)
        value = self.getValue(dc)
        if value:
            value = formatter.format(value)
        return value


class LinkColumn(Column):
    """Name column."""

    header = _('Name')
    linkName = None
    linkTarget = None
    linkContent = None
    linkCSS = None

    def getLinkURL(self, item):
        """Setup link url."""
        if self.linkName is not None:
            return '%s/%s' % (absoluteURL(item, self.request), self.linkName)
        return absoluteURL(item, self.request)

    def getLinkCSS(self, item):
        """Setup link css."""
        return self.linkCSS and ' css="%s"' % self.linkCSS or ''

    def getLinkTarget(self, item):
        """Setup link css."""
        return self.linkTarget and ' target="%s"' % self.linkTarget or ''

    def getLinkConent(self, item):
        """Setup link content."""
        return self.linkContent or api.getName(item)

    def renderCell(self, item):
        # setup a tag
        return '<a href="%s"%s%s>%s</a>' % (self.getLinkURL(item),
            self.getLinkTarget(item), self.getLinkCSS(item),
            self.getLinkConent(item))


class ContentsLinkColumn(LinkColumn):
    """Link pointing to contents.html."""

    linkName = 'contents.html'


class IndexLinkColumn(LinkColumn):
    """Link pointing to index.html."""

    linkName = 'index.html'


class EditLinkColumn(LinkColumn):
    """Link pointing to edit.html."""

    linkName = 'edit.html'
