# -*- coding: utf-8 -*-

import grok

from ZODB.broken import PersistentBroken
from zope.interface import Interface
from zope.component import queryMultiAdapter
from zope.app.container.interfaces import IContainer

from dolmen.app import security, layout
from dolmen.app.container import mf as _
from megrok.z3ctable import LinkColumn, ModifiedColumn, table

grok.templatedir("templates")


class FolderListing(layout.TablePage, layout.ContextualMenuEntry):
    grok.title(_(u"Content"))
    grok.context(IContainer)
    grok.require(security.CanListContent)
    
    batchSize = 20
    startBatchingAt = 20
    cssClassEven = u'even'
    cssClassOdd = u'odd'
    cssClasses = {'table': 'listing sortable'}
    sortOn = None
    
    @property
    def values(self):
        return self.context.values()

    def update(self):
        layout.TablePage.update(self)
        self.table = self.renderTable()


class Title(LinkColumn):
    """Display the name of the content item
    """
    table(FolderListing)
    grok.context(Interface)
    grok.name('folderlisting.title')

    weight = 10
    header = _(u"Title")

    def renderCell(self, item):
        if isinstance(item, PersistentBroken):
            return "Broken item: " + item.__Broken_state__.get('__name__')
        
        title = LinkColumn.renderCell(self, item)
        iconview = queryMultiAdapter(
            (item, self.table.request),
            name = "contenttype_icon"
            )
        if iconview is not None:
            return "%s&nbsp;%s" % (iconview(), title)
        return title


class ModificationDate(ModifiedColumn):
    """Display the name of the content item
    """
    table(FolderListing)
    grok.context(Interface)
    grok.name('folderlisting.modified')

    weight = 20
    header = _(u"Modified")
