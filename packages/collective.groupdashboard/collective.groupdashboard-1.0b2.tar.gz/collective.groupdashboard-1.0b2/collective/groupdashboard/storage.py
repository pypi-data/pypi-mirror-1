from five import grok

from plone.app.portlets.storage import PortletAssignmentMapping
from collective.groupdashboard.interfaces import IGroupPortletAssignmentMapping

from plone.app.portlets.interfaces import IPortletPermissionChecker

from AccessControl import getSecurityManager, Unauthorized
from Acquisition import aq_inner

# Provide a specific storage for group dashboard portlets with its own
# security checker

class GroupPortletAssignmentMapping(PortletAssignmentMapping):
    """An assignment mapping for user/dashboard portlets
    """

    grok.implements(IGroupPortletAssignmentMapping)
    
    @property
    def id(self):
        manager = self.__manager__
        key = self.__name__

        return "++groupdashboard++%s+%s" % (manager, key,)

class GroupPortletAssignmentChecker(grok.Adapter):
    """Check the permisssion for editing group portlets
    """
    
    grok.implements(IPortletPermissionChecker)
    grok.context(IGroupPortletAssignmentMapping)
    
    def __call__(self):
        sm = getSecurityManager()
        context = aq_inner(self.context)

        if not sm.checkPermission("collective.groupdashboard: Edit group dashboard", context):
            raise Unauthorized("You are not allowed to manage group portlets")