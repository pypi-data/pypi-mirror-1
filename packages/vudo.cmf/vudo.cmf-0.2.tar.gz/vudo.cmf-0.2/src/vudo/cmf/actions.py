from zope import component
from zope import interface

from repoze.bfg.traversal import model_url
from repoze.bfg.interfaces import IRequest

from vudo.cmf import MessageFactory as _

import interfaces

class Action(object):
    interface.implements(interfaces.IAction)

    name = None
    
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __repr__(self):
        return '<Action name="%s" url="%s">' % (
            self.name, self.url)
        
    @property
    def url(self):
        return model_url(self.context, self.request, self.name)

class Edit(Action):
    component.adapts(interfaces.IContent, IRequest)
    
    name = "@@edit"
    title = _("Edit")
    
class Add(Action):
    component.adapts(interfaces.IContainer, IRequest)
    
    name = "@@add"
    title = _("Add")
