from zope.component import getUtility, getMultiAdapter

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.storage import PortletAssignmentMapping
from collective.portlet.image import imageportlet
from Products.CMFPlone.tests import dummy

from collective.portlet.image.tests.base import TestCase


class TestPortlet(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))

    def test_portlet_type_registered(self):
        portlet = getUtility(IPortletType, name='collective.portlet.image.ImagePortlet')
        self.assertEquals(portlet.addview, 'collective.portlet.image.ImagePortlet')

    def test_interfaces(self):
        # TODO: Pass any keyword arguments to the Assignment constructor
        portlet = imageportlet.Assignment()
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def test_invoke_add_view(self):
        portlet = getUtility(IPortletType, name='collective.portlet.image.ImagePortlet')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)
        
        # for now we just add a dummy image
        addview.createAndAdd(data={'image':dummy.Image()})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0], imageportlet.Assignment))

    # NOTE: This test can be removed if the portlet has no edit form
    def test_invoke_edit_view(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = imageportlet.Assignment()
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, imageportlet.EditForm))

    def test_obtain_renderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)

        # TODO: Pass any keyword arguments to the Assignment constructor
        assignment = imageportlet.Assignment(image=dummy.Image())

        renderer = getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, imageportlet.Renderer))

class TestRenderer(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))

    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)

        # TODO: Pass any default keyword arguments to the Assignment constructor
        assignment = assignment or imageportlet.Assignment()
        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)

    def test_render(self):
        """
        for now it outputs something like 
        
        <dl class="portlet portletImagePortlet">

            <dt class="portletHeader">
                <span class="portletTopLeft"></span>

                <img src="http://nohost/plone/++contextportlets++plone.rightcolumn//edit/@@file/image/dummy.gif" />        
        
                Image portlet
                <span class="portletTopRight"></span>
            </dt>

            <dd class="portletItem odd">
                Body text
            </dd>

            <dd class="portletFooter">
                <span class="portletBotomLeft"></span>
                <span>
                   Footer
                </span>
                <span class="portletBottomRight"></span>
            </dd>

        </dl>
        """

        # TODO: Pass any keyword arguments to the Assignment constructor
        r = self.renderer(context=self.portal, assignment=imageportlet.Assignment(image=dummy.Image()))
        r = r.__of__(self.folder)
        r.update()
        
        output = r.render()

        # TODO: self.data.__name__ returns empty '' when running the test - why ? 
        # - perhaps its because the renderer function dont really do / make the 
        # portlet mapping in the manager. 
        # 
        # set it up.

        print output
        # TODO: Test output




def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
