from zope import interface
from zope import schema

import zope.schema.interfaces
import zope.schema.vocabulary

import z3c.formwidget.query.interfaces
import Products.CMFCore.utils

from collective.formwidget.uberselect import MessageFactory as _

class ArchetypesContentSource(object):
    interface.implements(z3c.formwidget.query.interfaces.IQuerySource)

    def __init__(self, context):
        self.context = context

    def __contains__(self, uid):
        """Verify the item exists."""
        
        return bool(self.catalog(uid=uid))
    
    def __iter__(self):
        return [].__iter__()

    @property
    def catalog(self):
        return Products.CMFCore.utils.getToolByName(self.context, 'portal_catalog')
        
    def getTermByToken(self, token):
        uid = token
        brain = self.catalog(UID=uid)[0]
        return self._term_for_brain(brain)

    def getTermByValue(self, value):
        uid = value
        brain = self.catalog(UID=uid)[0]
        return self._term_for_brain(brain)
    
    def search(self, query_string, limit=20):
        brains = self.catalog(SearchableText=query_string)[:limit]
        return map(self._term_for_brain, brains)

    def _term_for_brain(self, brain):
        return zope.schema.vocabulary.SimpleTerm(brain.UID, brain.UID, brain.Title)

class ArchetypesContentSourceBinder(object):
    interface.implements(zope.schema.interfaces.IContextSourceBinder)

    def __call__(self, context):
        return ArchetypesContentSource(context)

