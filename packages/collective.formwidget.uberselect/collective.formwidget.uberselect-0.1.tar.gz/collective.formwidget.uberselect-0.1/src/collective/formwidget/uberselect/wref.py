from zope import interface

from Products.CMFCore import utils as cmfutils

import persistent.wref

def uid2wref(field):
    class Adapter(object):
        interface.implements(field.interface)

        def __init__(self, context):
            self.context = context

    def _get_items(self):
        items = filter(None, (wref() for wref in self.context.items))
        return [item.UID() for item in items]

    def _set_items(self, uids):
        catalog = cmfutils.getToolByName(self.context, 'portal_catalog')
        brains = catalog(UID=tuple(uids))
        items = [brain.getObject() for brain in brains]
        self.context.items = map(persistent.wref.WeakRef, items)

    setattr(Adapter, field.__name__, property(_get_items, _set_items))
    return Adapter
