from zope.component import getUtility, getMultiAdapter
from zope.app.component.hooks import setHooks, setSite
from zope.component.interfaces import IFactory
from zope.event import notify

from zExceptions import Unauthorized

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRetriever
from plone.portlets.interfaces import IPortletType
from plone.portlets.constants import USER_CATEGORY
from plone.portlets.utils import hashPortletInfo

from plone.app.portlets.utils import assignment_mapping_from_key
from plone.app.portlets.tests.base import PortletsTestCase

from Products.CMFCore.utils import getToolByName
from Products.PluggableAuthService.events import PrincipalCreated
from Products.PluggableAuthService.PropertiedUser import PropertiedUser

class TestiDashboard(PortletsTestCase):

    def afterSetUp(self):
        setHooks()
        setSite(self.portal)

    def test_drag_and_drop(self):
        pm = getToolByName(self.portal, 'portal_membership')
        key = pm.getAuthenticatedMember().id

        movePortlet = self.portal.restrictedTraverse('@@movePortlet')
        for i in range(1,3):
            manager = u'plone.dashboard%d' % i

            mapping = assignment_mapping_from_key(self.portal,
                manager_name=manager, category=USER_CATEGORY, key=key)

            portlet = mapping['news']
            portlet_hash = hashPortletInfo(dict(manager=manager,
                                                category=USER_CATEGORY,
                                                key=key, 
                                                name=portlet.__name__))
        
            new_manager = u'plone.dashboard%d' % (i+1)
            portlet_hash = movePortlet(portlet_hash, new_manager, '')

            new_mapping = assignment_mapping_from_key(self.portal,
                manager_name=new_manager, category=USER_CATEGORY, key=key)

            self.failUnless('news' in new_mapping)

        portlet_hash = movePortlet(portlet_hash, 'plone.dashboard1', '')
        mapping = assignment_mapping_from_key(self.portal,
            manager_name='plone.dashboard1', category=USER_CATEGORY, key=key)
        self.failUnless('news' in mapping)

    def test_portlet_delete(self):
        manager = 'plone.dashboard1'
        pm = getToolByName(self.portal, 'portal_membership')
        key = pm.getAuthenticatedMember().id
        mapping = assignment_mapping_from_key(self.portal,
            manager_name=manager, category=USER_CATEGORY, key=key)
        portlet = mapping['news']
        portlet_hash = hashPortletInfo(dict(manager=manager,
                                            category=USER_CATEGORY,
                                            key=key, 
                                            name=portlet.__name__))

        removePortlet = self.portal.restrictedTraverse('@@removePortlet')
        removePortlet(portlet_hash)
        mapping = assignment_mapping_from_key(self.portal,
            manager_name=manager, category=USER_CATEGORY, key=key)

        self.failIf('news' in mapping)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestiDashboard))
    return suite

