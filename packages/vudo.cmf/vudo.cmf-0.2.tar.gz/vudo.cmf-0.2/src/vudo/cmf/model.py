from zope import event

from zope.lifecycleevent import ObjectCreatedEvent
from zope.lifecycleevent import ObjectModifiedEvent
from zope.location.interfaces import ILocation

from vudo.cmf.events import ObjectAddedEvent
from vudo.cmf.events import ObjectMovedEvent
from vudo.cmf.events import ObjectRemovedEvent
from vudo.cmf.events import ObjectBeforeModifiedEvent

class ContentEventSupport(object):
    def __init__(self, *args, **kwargs):
        super(ContentEventSupport, self).__init__(*args, **kwargs)
        if ILocation.providedBy(self):
            self.__name__ = self.__parent__ = None            
        event.notify(ObjectCreatedEvent(self))

class ContainerEventSupport(ContentEventSupport):
    def __setitem__(self, name, obj):
        if self.get(name) is obj:
            return
        
        event.notify(ObjectBeforeModifiedEvent(obj))
        event.notify(ObjectBeforeModifiedEvent(self))
        
        old_parent = getattr(obj, '__parent__', None)
        super(ContainerEventSupport, self).__setitem__(name, obj)

        obj.__name__ = name
        obj.__parent__ = self

        if old_parent is None:
            event.notify(ObjectAddedEvent(obj))
        else:
            event.notify(ObjectMovedEvent(obj, old_parent))

        event.notify(ObjectModifiedEvent(self))

    def __delitem__(self, name):
        obj = self.get(name)
        if obj is not None:
            old_parent = obj.__parent__
        super(ContainerEventSupport, self).__delitem__(name)
        event.notify(ObjectRemovedEvent(obj, old_parent))
        
