## Controller Python Script "login_next"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Login next actions
##

from Products.CMFPlone import PloneMessageFactory as PMF
from xm.theme import xmMessageFactory as _
from DateTime import DateTime
import ZTUtils

REQUEST = context.REQUEST

util = context.plone_utils
membership_tool=context.portal_membership
if membership_tool.isAnonymousUser():
    REQUEST.RESPONSE.expireCookie('__ac', path='/')
    util.addPortalMessage(PMF(u'Login failed'), 'error')
    return state.set(status='failure')

util.addPortalMessage(PMF(u'Welcome! You are now logged in.'))

# Get all projects, sorted on modification date.
catalog = context.portal_catalog
projectbrains = catalog.searchResults(portal_type='Project',
                                      sort_on='modified',
                                      sort_order='reverse')

if len(projectbrains) == 1:
    # If there is only 1 project -> redirect directly
    return REQUEST.RESPONSE.redirect(projectbrains[0].getURL())
elif len(projectbrains) > 1:
    # If there is a cookie with a last project, use that project.
    cookies = REQUEST.cookies
    if 'last_project' in cookies:
        for projectbrain in projectbrains:
            if projectbrain.id == cookies['last_project']:
                util.addPortalMessage(_(u'You have been redirected to the '
                                        u'last project you visited.'))
                return REQUEST.RESPONSE.redirect(projectbrain.getURL())

    # Now we'll have smart...
    # For customers: show the most recent project.
    member = membership_tool.getAuthenticatedMember()
    memberid = member.id
    projectbrain = projectbrains[0]
    if 'Customer' in member.getRolesInContext(
        projectbrain.getObject()):
        next_url = projectbrains[0].getURL()
    else:
        # For others: pick the most recent project with tasks assigned to
        # the user.
        for projectbrain in projectbrains:
            searchpath = projectbrain.getPath()
            taskbrains = catalog.searchResults(portal_type=['Task',
                                                            'PoiTask'],
                                               getAssignees=memberid,
                                               review_state=('open', 'to-do'),
                                               path=searchpath)
            if len(taskbrains) > 0:
                next_url = taskbrains[0].getURL()
                break
        if not next_url:
            next_url = context.portal_url.getPortalObject().absolute_url()
    util.addPortalMessage(_(u'You have been redirected to your '
                            u'most recent project.'))
else:
    next_url = context.portal_url.getPortalObject().absolute_url()

# redirect immediately
return REQUEST.RESPONSE.redirect(next_url)
