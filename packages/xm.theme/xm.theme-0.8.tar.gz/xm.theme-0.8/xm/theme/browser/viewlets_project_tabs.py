from Acquisition import aq_inner
from DateTime import DateTime
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize.view import memoize

from xm.theme import xmMessageFactory as _

TAB_SELECTED = u'selected'
TAB_NORMAL = u''


class XMProjectTabsViewlet(ViewletBase):
    """A view to render the Project Tabs Manager."""

    render = ViewPageTemplateFile('templates/project_tabs_viewlet.pt')

    @memoize
    def get_project(self):
        """Return the project of this context.
        Also set a cookie with the project id. This can be used to redirect
        after logging in.
        """
        try:
            project = aq_inner(self.context).getProject()
            expires = (DateTime() + 90).toZone('GMT').rfc822()
            self.request.response.setCookie('last_project',
                                            project.getId(),
                                            path = '/',
                                            expires = expires)
        except AttributeError:
            project = None
        return project

    @memoize
    def get_iteration(self):
        """Return the iteration of this context."""
        try:
            iteration = aq_inner(self.context).getIteration()
        except AttributeError:
            iteration = None
        return iteration


class ProjectTabsBaseViewlet(ViewletBase):
    """Base viewlet for the project tabs."""

    render = ViewPageTemplateFile('templates/project_tab.pt')

    def __init__(self, context, request, view, manager):
        super(ProjectTabsBaseViewlet, self).__init__(context, request,
                                                     view, manager)
        self.project = view.get_project()
        self.iteration = view.get_iteration()

    def update(self):
        """Update method for the viewlet."""
        self.available = self._is_available()
        self.element_id = self._get_id()
        self.tab_class = self._get_tab_class()
        self.title = self._get_title()
        self.description = self._get_description()
        self.url = self._get_url()

    @memoize
    def _is_available(self):
        """Return whether the viewlet/tab is available."""
        return self.project and self._get_items()

    @memoize
    def _get_id(self):
        """Return the id for the element of the tab."""
        return 'portaltab-%s' % self._get_title().replace(' ', '_')

    @memoize
    def _get_tab_class(self):
        """Return the class for the tab."""
        value = TAB_NORMAL
        items = self._get_items()
        for item in items:
            if item['selected']:
                value = TAB_SELECTED
        return value

    @memoize
    def _get_title(self):
        """Return the title of the tab."""
        return _(u'Example')

    @memoize
    def _get_description(self):
        """Return a description of the tab."""
        return _(u'Example tab')

    @memoize
    def _get_url(self):
        """Return the url for the tab."""
        return '#'

    @memoize
    def _get_items(self):
        """Return the items."""
        return None


class CurrentIterationsViewlet(ProjectTabsBaseViewlet):
    """Viewlet for the current iterations tab."""

    @memoize
    def _get_title(self):
        """Return the title of the tab."""
        if len(self._get_items()) > 1:
            return _(u'Current&hellip;')
        else:
            return _(u'Current')

    @memoize
    def _get_description(self):
        """Helper function which returns the default description of the tab."""
        items = self._get_items()
        if len(items) > 1:
            return _(u'Current iterations')
        elif len(items) == 1:
            return '"%s"' % items[0]['title']
        else:
            return ''

    @memoize
    def _get_url(self):
        """Return the url for the tab."""
        items = self._get_items()
        if len(items) > 1:
            return '%s/project_content?type=iteration&state=current' % (
                self.project.absolute_url())
        elif len(items) == 1:
            return items[0]['url']
        else:
            return ''

    @memoize
    def _get_items(self):
        """Return the items for the tab."""
        if not self.project:
            return []
        current = self.iteration
        cfilter = dict(portal_type = 'Iteration',
                       review_state = 'in-progress')
        brains = self.project.getFolderContents(cfilter)
        result = []
        for brain in brains:
            selected = False
            if current and current.getId() == brain.id:
                selected = True
            result.append(dict(
                title = brain.Title,
                url = brain.getURL(),
                selected = selected,
                ))
        return result


class OpenIterationsViewlet(ProjectTabsBaseViewlet):
    """Viewlet for the open iterations tab."""

    @memoize
    def _get_title(self):
        """Return the title of the tab."""
        if len(self._get_items()) > 1:
            return _(u'Open&hellip;')
        else:
            return _(u'Open')

    @memoize
    def _get_description(self):
        """Helper function which returns the default description of the tab."""
        items = self._get_items()
        if len(items) > 1:
            return _(u'Open iterations')
        elif len(items) == 1:
            return '"%s"' % items[0]['title']
        else:
            return ''

    @memoize
    def _get_url(self):
        """Return the url for the tab."""
        items = self._get_items()
        if len(items) > 1:
            return '%s/project_content?type=iteration&state=open' % (
                self.project.absolute_url())
        elif len(items) == 1:
            return items[0]['url']
        else:
            return ''

    @memoize
    def _get_items(self):
        """Return the items for the tab."""
        if not self.project:
            return []
        current = self.iteration
        cfilter = dict(portal_type = 'Iteration',
                       review_state = 'new')
        brains = self.project.getFolderContents(cfilter)
        result = []
        for brain in brains:
            selected = False
            if current and current.getId() == brain.id:
                selected = True
            result.append(dict(
                title = brain.Title,
                url = brain.getURL(),
                selected = selected,
                ))
        return result


class ClosedIterationsViewlet(ProjectTabsBaseViewlet):
    """Viewlet for the closed iterations tab."""

    @memoize
    def _get_title(self):
        """Return the title of the tab."""
        if len(self._get_items()) > 1:
            return _(u'Closed&hellip;')
        else:
            return _(u'Closed')

    @memoize
    def _get_description(self):
        """Helper function which returns the default description of the tab."""
        items = self._get_items()
        if len(items) > 1:
            return _(u'Closed iterations')
        elif len(items) == 1:
            return '"%s"' % items[0]['title']
        else:
            return ''

    @memoize
    def _get_url(self):
        """Return the url for the tab."""
        items = self._get_items()
        if len(items) > 1:
            return '%s/project_content?type=iteration&state=closed' % (
                self.project.absolute_url())
        elif len(items) == 1:
            return items[0]['url']
        else:
            return ''

    @memoize
    def _get_items(self):
        """Return the items for the tab."""
        if not self.project:
            return []
        current = self.iteration
        cfilter = dict(portal_type = 'Iteration',
                       review_state = ('completed', 'invoiced'))
        brains = self.project.getFolderContents(cfilter)
        result = []
        for brain in brains:
            selected = False
            if current and current.getId() == brain.id:
                selected = True
            result.append(dict(
                title = brain.Title,
                url = brain.getURL(),
                selected = selected,
                ))
        return result
