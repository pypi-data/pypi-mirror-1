from zope import interface
from zope import schema

from zope.dublincore.interfaces import IDCDescriptiveProperties
from zope.dublincore.interfaces import IDCTimes
from zope.component.interfaces import IObjectEvent
from zope.location.interfaces import ILocation

import repoze.bfg.httprequest

from repoze.bfg.interfaces import IRequest

IGetRequest = IRequest(
    {'http_accept': 'text/html', 'request_method': 'get'})

IPostRequest = IRequest(
    {'http_accept': 'text/html', 'request_method': 'post'})

IAjaxGetRequest = IRequest(
    {'request_method': 'get', 'http_x_requested_with': 'xmlhttprequest'})

IAjaxPostRequest = IRequest(
    {'request_method': 'post', 'http_x_requested_with': 'xmlhttprequest'})

class IContentManager(IDCDescriptiveProperties):
    """Manages a content item. This is the formal interface that
    library code should rely on.

    Realizations of this interface may introduce convention with
    regards to the content classes they represent, but these should
    not be relied on outside this context.

    Note that this interface includes descriptive properties. These
    may be used by user interfaces to display information about the
    content class.
    """

    context = interface.Attribute(
        """The content object being managed.""")

    type_id = interface.Attribute(
        """Global type id for this content class. This value must be
        an integer.""")

    def get_url(request=None):
        """Return a URL (may be relative to current location) for this
        content item."""

    def get_actions(request=None):
        """Return actions (see ``IAction``) for this content item."""
        
    def get_allowed_types():
        """Returns a list or tuple of content factories (classes) which are
        addable to this object."""

    def resolve_type(type_id):
        """Returns the content class for a given `type_id`."""
        
    def auto_generate_id():
        """Returns a content id (name) for this content to be used for
        content traversal."""

class IContentMetadata(interface.Interface):
    """Provides metadata formatting services."""

    def format_creation_date(long_format=False):
        """Return a translatable formatted date."""

class IContent(IDCTimes):
    """Content objects are models which have a unique identifier and
    carry a timestamp for creation and modification."""

    __meta__ = interface.Attribute(
        """Content class metadata; this must be a dictionary. It's
        recommended to provide at least ``title`` and ``description``
        which should be unicode strings or translatable i18n messages.""")

    uuid = interface.Attribute(
        """Unique content identifier.""")

class IContainer(IContent):
    """Content may contain other content items using the dictionary
    mapping protocol."""

class IModel(IContent, ILocation, IDCDescriptiveProperties):
    """Models are traversable content objects."""    

class IPage(IModel):
    """A page application which represents a web page; it displays
    zero or more content items (widgets), managed in the ``content``
    attribute."""

    content = interface.Attribute(
        """List or tuple of content items to be displayed on this
        page.""")

class IForm(interface.Interface):
    """Content form. This interface is modelled after the form-class
    of ``repoze.formapi``."""
    
    data = interface.Attribute(
        """Form data object.""")

class IAction(interface.Interface):
    """Represents a content action."""

    url = interface.Attribute(
        """The URL which this action corresponds to.""")

    title = interface.Attribute(
        """Action title.""")

class IObjectMovedEvent(IObjectEvent):
    """Issued when an object has been moved."""

    old_parent = interface.Attribute(
        """The parent to which the object is moved from, if
        applicable.""")

class IObjectAddedEvent(IObjectMovedEvent):
    """Issued when an object has been added."""

class IObjectRemovedEvent(IObjectEvent):
    """Issued when an object has been removed."""

class IObjectBeforeModifiedEvent(IObjectEvent):
    """Issued before an object is modified."""
