from plone.theme.interfaces import IDefaultPloneLayer
from zope.viewlet.interfaces import IViewletManager
from zope.publisher.interfaces.browser import IBrowserView
from zope.interface import Interface
from zope.interface import directlyProvides
from zope.contentprovider.interfaces import ITALNamespaceData
from zope.schema import Text


class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """


class IProjectTabsManager(IViewletManager):
    """A viewlet manager which will be used to display the tabs for
    a project.
    """


class IProjectContentView(IBrowserView):
    """Return information about the contents of a project."""

    def requested_type():
        """Return the requested portal type."""

    def requested_state():
        """Return the requested state."""

    def title():
        """Return the title for the page."""


class IProjectContentProvider(Interface):
    """Content provider to show the contents of a project."""

    portal_type = Text(title = u'Portal type to filter on.')
    state = Text(title = u'State to filter on.')

    def iterations():
        """Return the iterations."""

directlyProvides(IProjectContentProvider, ITALNamespaceData)
