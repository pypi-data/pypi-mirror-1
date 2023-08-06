from zope import interface
from zope import component

import os
import utils
import metadata
import interfaces

from repoze.bfg.interfaces import IRequest
from repoze.bfg.skins.interfaces import ISkinApi
from repoze.bfg.skins.interfaces import ISkinTemplate

from plone.transforms.interfaces import ITransformEngine

@interface.implementer(ISkinApi)
@component.adapter(interfaces.IContent, IRequest, ISkinTemplate)
def get_transform(context, request, template):
    """MIME-type conversion and transformation from templates."""

    def transform(data, source_mimetype=None, mimetype=None, options={}):
        engine = component.getUtility(ITransformEngine)
        result = engine.transform(
            (data,), source_mimetype, mimetype, options=options)
        return u"".join(result.data)

    return transform

@interface.implementer(ISkinApi)
@component.adapter(interfaces.IContent, IRequest, ISkinTemplate)
def get_form(context, request, template):
    """Access to forms from skin templates. If a component with the
    name of the template is not found, a default component lookup is
    attempted."""

    form = component.queryMultiAdapter(
        (context, request), interfaces.IForm, name=template.name)

    if form is not None:
        return form
    
    return component.getMultiAdapter(
        (context, request), interfaces.IForm)

@interface.implementer(ISkinApi)
@component.adapter(interfaces.IContent, IRequest, ISkinTemplate)
def get_content_api(context, request, template):
    """Application programming interface for content objects."""

    factory = component.getSiteManager().adapters.lookup(
        (interface.providedBy(context),), interfaces.IContentManager)

    return factory(context, request)

@interface.implementer(ISkinApi)
@component.adapter(interfaces.IContent, IRequest, ISkinTemplate)
def get_content_url(context, request, template):
    """Application programming interfaces for getting a URL of a content
    object."""
    return interfaces.IContentManager(context).get_url(request)

@interface.implementer(ISkinApi)
@component.adapter(interfaces.IModel, IRequest, ISkinTemplate)
def get_action_from_request(context, request, template):
    def get_action(request=request):
        return utils.get_action_from_request(request)
    return get_action

@interface.implementer(ISkinApi)
@component.adapter(interfaces.IModel, IRequest, ISkinTemplate)
def get_metadata(context, request, template):
    return metadata.Metadata(context)

