from zope import interface
from zope import component
from zope import event

from zope.lifecycleevent import ObjectCreatedEvent
from zope.lifecycleevent import ObjectModifiedEvent

from repoze.bfg.interfaces import IView
from repoze.bfg.interfaces import IRequest

import interfaces
import webob
import utils

from vudo import cmf

class EditViewFactory(object):
    component.adapts(interfaces.IContent, interfaces.IPostRequest)
    
    def __init__(self, get_request_interface):
        self.get_request_interface = get_request_interface

    def __call__(self, context, request):
        form = component.getMultiAdapter(
            (context, request), interfaces.IForm)

        if form.validate():
            status = form()
            event.notify(ObjectModifiedEvent(context))
            
        name = utils.get_action_from_request(request)
        view = component.getSiteManager().adapters.lookup(
            (interface.providedBy(context), self.get_request_interface),
            IView, name=name)
        
        if view is None or view is self:
            raise webob.exc.HTTPNotFound(request.url)
    
        return view(context, request, form=form)
page_edit_view = EditViewFactory(interfaces.IGetRequest)

class AjaxEditViewFactory(EditViewFactory):
    component.adapts(interfaces.IContent, interfaces.IAjaxPostRequest)
ajax_edit_view = AjaxEditViewFactory(interfaces.IAjaxGetRequest)

class AddViewFactory(object):
    component.adapts(interfaces.IContent, interfaces.IPostRequest)

    def __init__(self, get_request_interface):
        self.get_request_interface = get_request_interface

    def __call__(self, context, request):
        create_form = cmf.form.AddForm(context, request)

        # create new content object
        obj = create_form.create_object()
        event.notify(ObjectCreatedEvent(obj))

        # look up form and apply data
        form = component.getMultiAdapter(
            (obj, request), interfaces.IForm)
        form.data.save()
        event.notify(ObjectModifiedEvent(obj))
        
        # auto-generate id (name)
        manager = interfaces.IContentManager(obj)
        name = obj.__name__ = manager.auto_generate_id()

        # add to container
        context[name] = obj
        obj.__parent__ = context
        event.notify(ObjectModifiedEvent(context))

        # redirect to default action
        default_action = manager.get_actions(request)[0]
        
        return webob.exc.HTTPFound(location=default_action.url)
page_add_view = AddViewFactory(interfaces.IGetRequest)
