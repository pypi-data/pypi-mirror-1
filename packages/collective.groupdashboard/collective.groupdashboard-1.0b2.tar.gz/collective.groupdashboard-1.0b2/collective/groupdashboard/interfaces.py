from zope.interface import Interface
from plone.portlets.interfaces import IPortletAssignmentMapping

class IGroupDashboardLayer(Interface):
    """Marker interface for requests when the group dashboard product is
    installed.
    """
    
class IGroupPortletAssignmentMapping(IPortletAssignmentMapping):
    """Group portlets storage. Has its own security checker.
    """