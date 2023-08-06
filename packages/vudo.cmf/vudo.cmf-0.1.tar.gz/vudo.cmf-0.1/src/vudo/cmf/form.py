from zope import interface
from zope import component
from zope import event

from repoze import formapi
from repoze.bfg.interfaces import IRequest

import utils
import events
import interfaces

from vudo.cmf import MessageFactory as _

class BaseForm(formapi.Form):
    """Form base class. Infers the form prefix from the request,
    e.g. the 'action' name."""
    
    interface.implements(interfaces.IForm)

    def __init__(self, context, request):
        prefix = utils.get_action_from_request(request)
        super(BaseForm, self).__init__(
            context=context, request=request, prefix=prefix)

class EditForm(BaseForm):
    """Content edit form."""

    @formapi.action
    def handle_save(self, data):
        """Save content."""

        event.notify(
            events.ObjectBeforeModifiedEvent(self.context))

        data.save()

        return _(
            u"Content updated at $M/$d-$g @ $r. Some changes may not be "
            "visible until you reload the page.",
            mapping=utils.datetimedict.today())

class AddForm(BaseForm):
    """Content add form."""

    component.adapts(interfaces.IContainer, IRequest)
    
    fields = {
        'type_id': int
        }

    def __init__(self, context, request):
        # instantiate form without passing a context
        super(AddForm, self).__init__(None, request)

        # set `context` as an internal variable
        self.context = context
        
    def create_object(self):
        """Creates a new object and returns it."""

        type_id = self.data['type_id']
        manager = interfaces.IContentManager(self.context)
        factory = manager.resolve_type(type_id)

        return factory()

class ModelForm(EditForm):
    component.adapts(interfaces.IModel, IRequest)

    fields = {
        'title': str,
        'description': str,
        }

