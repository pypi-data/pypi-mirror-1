#!/usr/bin/python
# -*- coding: utf-8 -*-

import grok
from grok import index
from dolmen.app.site import IDolmen
from dolmen.content import IBaseContent
from zope.index.text.interfaces import ISearchableText


class BaseIndexes(grok.Indexes):
    """Indexes the title and the content type of an IBaseContent content.
    """
    grok.site(IDolmen)
    grok.context(IBaseContent)

    title = index.Text()
    content_type = index.Field(attribute='__content_type__')


class SearchableIndex(grok.Indexes):
    """Indexes the searchable text of an ISearchableText content.
    """
    grok.site(IDolmen)
    grok.context(ISearchableText)

    searchabletext = index.Text(attribute="getSearchableText")


class BaseSearchable(grok.Adapter):
    """Provides the needed ISearchableText methods for and IBaseContent.
    """
    grok.implements(ISearchableText)
    grok.context(IBaseContent)

    def getSearchableText(self):
        return self.context.title


__all__ = ['BaseIndexes', 'SearchableIndex', 'BaseSearchable']
