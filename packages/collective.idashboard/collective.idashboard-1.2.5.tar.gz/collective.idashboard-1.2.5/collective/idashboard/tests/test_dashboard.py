import zope.interface
from zope import component
from zope.publisher.browser import TestRequest

from plone.portlets.constants import USER_CATEGORY
from plone.portlets.utils import hashPortletInfo
from plone.browserlayer import utils

from plone.app.portlets.utils import assignment_mapping_from_key

from Products.CMFCore.utils import getToolByName

from collective.idashboard.tests.base import iDashboardTestCase
from collective.idashboard.interfaces import IIDashboardLayer

class TestiDashboard(iDashboardTestCase):

    def afterSetUp(self):
        """ """
        self.assertTrue(IIDashboardLayer in utils.registered_layers())

        # Make sure that convergence layer is applied on the test request,
        # so that our custom views kick in
        zope.interface.directlyProvides(
            self.portal.REQUEST, 
            [IIDashboardLayer] + list(zope.interface.directlyProvidedBy(self.portal.REQUEST))
            )


    def test_drag_and_drop(self):
        pm = getToolByName(self.portal, 'portal_membership')
        key = pm.getAuthenticatedMember().id

        zope.interface.classImplements(TestRequest, IIDashboardLayer)

        movePortlet = component.getMultiAdapter(
                                    (self.portal, self.portal.REQUEST),
                                    name='movePortlet'
                                    )

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

        removePortlet = component.getMultiAdapter(
                                    (self.portal, self.portal.REQUEST),
                                    name='removePortlet'
                                    )

        removePortlet(portlet_hash)
        mapping = assignment_mapping_from_key(self.portal,
            manager_name=manager, category=USER_CATEGORY, key=key)

        self.failIf('news' in mapping)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestiDashboard))
    return suite

