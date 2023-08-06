from unittest import defaultTestLoader

from zope.component import getUtility

from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

from zope.component import getAllUtilitiesRegisteredFor
from plone.browserlayer.interfaces import ILocalBrowserLayerType

from collective.groupdashboard.interfaces import IGroupDashboardLayer

from Acquisition import aq_parent
from AccessControl import Unauthorized

from plone.portlets.constants import GROUP_CATEGORY
from plone.portlets.interfaces import IPortletManager

from plone.app.portlets.interfaces import IPortletPermissionChecker
from plone.app.portlets.portlets import classic

@onsetup
def setup_product():
    import collective.groupdashboard
    zcml.load_config('configure.zcml', collective.groupdashboard)

setup_product()
ptc.setupPloneSite(products=['collective.groupdashboard'])

class TestSetup(ptc.PloneTestCase):
    
    def test_browserlayer_installed(self):
        layers = list(getAllUtilitiesRegisteredFor(ILocalBrowserLayerType))
        self.failUnless(IGroupDashboardLayer in layers)
    
    def test_view_permission(self):
        self.setRoles(('Member',))
        self.failUnless(self.portal.portal_membership.checkPermission('collective.groupdashboard: View dashboard', self.portal))
        self.setRoles(('Anonymous',))
        self.failIf(self.portal.portal_membership.checkPermission('collective.groupdashboard: View dashboard', self.portal))
        
    def test_edit_permission(self):
        self.setRoles(('Manager',))
        self.failUnless(self.portal.portal_membership.checkPermission('collective.groupdashboard: Edit group dashboard', self.portal))
        self.setRoles(('Member',))
        self.failIf(self.portal.portal_membership.checkPermission('collective.groupdashboard: Edit group dashboard', self.portal))

class TestTraversal(ptc.PloneTestCase):
    
    def testGroupDashboardNamespace(self):
        assignment = classic.Assignment()
        manager = getUtility(IPortletManager, name='plone.dashboard1')
        mapping = self.portal.restrictedTraverse('++groupdashboard++plone.dashboard1+Reviewers')
        self.failUnless(aq_parent(mapping) is self.portal)
        mapping['foo'] = assignment
        self.failUnless(manager[GROUP_CATEGORY]['Reviewers']['foo'] is assignment)
        self.assertEquals('++groupdashboard++plone.dashboard1+Reviewers', mapping.id)
        
    def test_checker(self):
        assignment = classic.Assignment()
        manager = getUtility(IPortletManager, name='plone.dashboard1')
        mapping = self.portal.restrictedTraverse('++groupdashboard++plone.dashboard1+Reviewers')
        
        checker = IPortletPermissionChecker(mapping)
        
        self.setRoles(('Manager',))
        checker() # no exception
        
        self.setRoles(('Member',))
        self.assertRaises(Unauthorized, checker)

def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)