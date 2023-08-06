from zope import interface
from zope import component

from zope.dublincore.interfaces import IDCDescriptiveProperties
from repoze.bfg.traversal import model_url

import datetime
import interfaces

class DefaultContentManager(object):
    """This is the default content manager implementation. It's
    conventional by nature; many options are readily customizable."""
    
    interface.implements(interfaces.IContentManager)
    component.adapts(interfaces.IContent)
    
    def __init__(self, context, request=None):
        self.context = context
        self._request = request

    @property
    def type_id(self):
        return id(type(self.context))

    @property
    def request(self):
        if self._request is None:
            raise ValueError(
                "Content manager is not bound to a request.")
        return self._request

    def get_url(self, request=None):
        return model_url(self.context, request or self.request)

    def get_actions(self, request=None):
        """Return content actions, sorted by name."""
        
        return [action for (name, action) in sorted(
            component.getAdapters(
            (self.context, request or self.request), interfaces.IAction),
            key=lambda (name, action): name)]
            
    def get_allowed_types(self):
        assert interfaces.IContainer.providedBy(self.context), \
               "Addable types only applies to container objects."

        return [{
            'metadata': factory.__meta__,
            'type_id': id(factory),
            } for factory in self.context.__allowed_types__]

    def resolve_type(self, type_id):
        for factory in self.context.__allowed_types__:
            if id(factory) == type_id:
                return factory

        raise LookupError(
            "Unable to find factory with id = '%s'." % type_id)

    def auto_generate_id(self):
        if IDCDescriptiveProperties.providedBy(self.context) and \
           bool(self.context.title):
            return self.context.title.lower().\
                   replace(' ', '-').\
                   replace(',', '')

        return 'id-%s' % \
               datetime.datetime.today().isoformat().replace(':', '.')
