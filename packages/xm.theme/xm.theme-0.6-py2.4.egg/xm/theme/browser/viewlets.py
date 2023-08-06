from zope.component import getMultiAdapter

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from plone.app.layout.viewlets.common import ViewletBase


class XMProjectHeaderViewlet(ViewletBase):
    render = ViewPageTemplateFile('templates/project_header.pt')

    def update(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.site_url = self.portal_state.portal_url()
        self.project_title = self._get_project_title()
        self.project_url = self._get_project_url()

    def _get_project(self):
        try:
            project = self.context.getProject()
        except AttributeError:
            project = None
        return project

    def _get_project_title(self):
        project = self._get_project()
        if project is not None:
            return project.title
        else:
            return u'Extreme Management'

    def _get_project_url(self):
        project = self._get_project()
        if project is not None:
            return project.absolute_url()
        else:
            return self.site_url


class XMSearchBoxViewlet(ViewletBase):
    render = ViewPageTemplateFile('templates/searchbox.pt')

    def update(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.site_url = self.portal_state.portal_url()
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        props = getToolByName(self.context, 'portal_properties')
        livesearch = props.site_properties.getProperty('enable_livesearch',
                                                       False)
        if livesearch:
            self.search_input_id = "searchGadget"
        else:
            self.search_input_id = ""

        folder = context_state.folder()
        self.folder_path = '/'.join(folder.getPhysicalPath())
        

class GoogleSearchViewlet(ViewletBase):

        render = ViewPageTemplateFile('templates/googlesearch.pt')
