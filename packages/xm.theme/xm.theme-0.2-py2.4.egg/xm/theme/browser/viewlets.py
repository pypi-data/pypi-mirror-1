from zope.component import getMultiAdapter
from AccessControl import getSecurityManager

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from plone.app.layout.viewlets.common import ViewletBase

from urllib import quote_plus


class XMPersonalBarViewlet(ViewletBase):
    """ A view that returns a list of active projects, in addition to the
    default personal_bar.
    """
    render = ViewPageTemplateFile('templates/xm_personal_bar.pt')

    def update(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        tools = getMultiAdapter((self.context, self.request),
                                name=u'plone_tools')

        sm = getSecurityManager()

        self.portal_url = portal_state.portal_url()

        self.user_actions = context_state.actions().get('user', None)

        plone_utils = getToolByName(self.context, 'plone_utils')
        self.getIconFor = plone_utils.getIconFor

        self.anonymous = portal_state.anonymous()

        if not self.anonymous:

            member = portal_state.member()
            userid = member.getId()

            if sm.checkPermission('Portlets: Manage own portlets',
                                  self.context):
                self.homelink_url = self.portal_url + '/dashboard'
            else:
                self.homelink_url = self.portal_url + '/author/' + \
                                    quote_plus(userid)

            member_info = tools.membership().getMemberInfo(member.getId())
            fullname = member_info.get('fullname', '')
            if fullname:
                self.user_name = fullname
            else:
                self.user_name = userid

        # The above is the default personal_bar code
        pview = getMultiAdapter((self.context, self.request),
                                name=u'myprojects')
        pbrains = pview.projectlist
        projects = []
        for pbrain in pbrains:
            projects.append(dict(title = pbrain.Title,
                                 url = pbrain.getURL(),
                                 description = pbrain.Description))
        self.my_projects = projects

        self.has_projects = False
        if len(self.my_projects) > 1:
            self.has_projects = True

        self.has_single_project = False
        if len(self.my_projects) == 1:
            self.has_single_project = True


class XMProjectHeaderViewlet(ViewletBase):
    render = ViewPageTemplateFile('templates/project_header.pt')

    def update(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.portal_url = portal_state.portal_url()
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
            return self.portal_url


class XMSearchBoxViewlet(ViewletBase):
    render = ViewPageTemplateFile('templates/searchbox.pt')

    def update(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')

        self.portal_url = portal_state.portal_url()

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
