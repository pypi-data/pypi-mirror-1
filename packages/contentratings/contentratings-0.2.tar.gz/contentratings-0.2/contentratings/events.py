from Acquisition import aq_base
from zope.interface import implements
from zope.app.event.objectevent import ObjectModifiedEvent
from contentratings.interfaces import IObjectUserRatedEvent
from contentratings.interfaces import IObjectEditorRatedEvent

class ObjectUserRatedEvent(ObjectModifiedEvent):
    """An event that will be used to trigger necessary actions on user rating
       changes"""
    implements(IObjectUserRatedEvent)

class ObjectEditorRatedEvent(ObjectModifiedEvent):
    """An event that will be used to trigger necessary actions on editor
       rating changes"""
    implements(IObjectEditorRatedEvent)

def reindexOnEditorRate(obj, event):
    if getattr(aq_base(obj), 'reindexObject', None) is not None:
        obj.reindexObject()