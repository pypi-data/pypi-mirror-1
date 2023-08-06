from zope import interface
from zope import component

from zope.component.interfaces import ObjectEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.location.interfaces import ILocation

import interfaces
import uuid

from datetime import datetime

@component.adapter(interfaces.IContent, IObjectCreatedEvent)
def assign_uid(obj, event):
    obj.uid = str(uuid.uuid1())

@component.adapter(interfaces.IContent, IObjectCreatedEvent)
def assign_dctimes(obj, event):
    obj.created = datetime.today()

class ObjectMovedEvent(ObjectEvent):
    interface.implements(interfaces.IObjectMovedEvent)

    def __init__(self, obj, old_parent=None):
        if old_parent is None:
            old_parent = obj.__parent__

        self.object = obj
        self.old_parent = old_parent
        
class ObjectAddedEvent(ObjectMovedEvent):
    interface.implements(interfaces.IObjectAddedEvent)

class ObjectRemovedEvent(ObjectMovedEvent):
    interface.implements(interfaces.IObjectRemovedEvent)

class ObjectBeforeModifiedEvent(ObjectMovedEvent):
    """An object will be modified; this event is issued immediately
    before an object is modified."""
    
    interface.implements(interfaces.IObjectBeforeModifiedEvent)
