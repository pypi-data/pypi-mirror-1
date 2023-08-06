from five import grok

from zope.component import getUtility, getMultiAdapter

from plone.portlets.interfaces import IPortletManager
from plone.portlets.constants import USER_CATEGORY, GROUP_CATEGORY

from plone.app.portlets.browser.interfaces import IManageDashboardPortletsView

from plone.memoize.instance import memoize

from zope.traversing.interfaces import ITraversable
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces.http import IHTTPRequest

from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot

from collective.groupdashboard.interfaces import IGroupDashboardLayer
from collective.groupdashboard.storage import GroupPortletAssignmentMapping

# Allow traversal to group portlet assignments

class GroupDashboardNamespace(grok.MultiAdapter):
    """Used to traverse to a portlet assignable for a group for the dashboard
    """
    
    grok.name('groupdashboard')
    grok.implements(ITraversable)
    grok.adapts(IPloneSiteRoot, IHTTPRequest)
    
    def __init__(self, context, request=None):
        self.context = context
        self.request = request
        
    def traverse(self, name, ignore):
        col, group = name.split('+')
        column = getUtility(IPortletManager, name=col)
        category = column[GROUP_CATEGORY]
        manager = category.get(group, None)
        if manager is None:
            manager = category[group] = GroupPortletAssignmentMapping(manager=col,
                                                                      category=GROUP_CATEGORY,
                                                                      name=group)                                                                            
        return manager

# Override dashboard view to have a different definition of an 'empty'
# dashboard, use a different 'view' permission and hide the 'edit' tab if
# the user lacks permission to change their own portlets.

class Dashboard(grok.View):
    """A group-aware version of the dashboard view
    """
    
    grok.context(IPloneSiteRoot)
    grok.layer(IGroupDashboardLayer)
    grok.name('dashboard')
    grok.require('collective.groupdashboard.ViewDashboard')
    
    def update(self):
        self.request.set('disable_border', True)
    
    @memoize
    def can_edit(self):
        return bool(getSecurityManager().checkPermission('Portlets: Manage own portlets', self.context))
    
    @memoize
    def empty(self):
        dashboards = [getUtility(IPortletManager, name=name) for name in
                        ['plone.dashboard1', 'plone.dashboard2', 'plone.dashboard3', 'plone.dashboard4']]
                        
        portal_membership = getToolByName(self.context, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        userid = member.getId()
                        
        num_portlets = 0
        for dashboard in dashboards:
            num_portlets += len(dashboard.get(USER_CATEGORY, {}).get(userid, {}))
            for groupid in member.getGroups():
                num_portlets += len(dashboard.get(GROUP_CATEGORY, {}).get(groupid, {}))
        return num_portlets == 0    

# Provide a "manage group dashboard" view

class Manage(grok.View):
    """A "manage" view for group dashboard portlets.
    """
    
    grok.implements(IManageDashboardPortletsView)
    
    grok.context(IPloneSiteRoot)
    grok.layer(IGroupDashboardLayer)
    grok.name('manage-group-dashboard')
    grok.require('collective.groupdashboard.EditGroupDashboard')
    
    @property
    def group(self):
        return self.request.get('key', None)
    
    def update(self):
        self.request.set('disable_border', True)
        if self.group is None:
            raise NotFound("Group must be specified via the 'key' request parameter")
    
    # IManagePortletsView implementation
    
    @property
    def category(self):
        return GROUP_CATEGORY
    
    @property
    def key(self):
        return self.group
    
    def getAssignmentMappingUrl(self, manager):
        baseUrl = str(getMultiAdapter((self.context, self.request), name='absolute_url'))
        return '%s/++groupdashboard++%s+%s' % (baseUrl, manager.__name__, self.group)

    def getAssignmentsForManager(self, manager):
        column = getUtility(IPortletManager, name=manager.__name__)
        category = column[GROUP_CATEGORY]
        mapping = category.get(self.group, None)
        if mapping is None:
            mapping = category[self.group] = GroupPortletAssignmentMapping(manager=manager.__name__,
                                                                           category=GROUP_CATEGORY,
                                                                           name=self.group)
        return mapping.values()