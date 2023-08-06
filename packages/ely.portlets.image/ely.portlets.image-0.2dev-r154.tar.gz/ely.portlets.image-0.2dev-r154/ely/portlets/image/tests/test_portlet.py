import os
from OFS.Image import Image
from zope.component import getUtility, getMultiAdapter

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.storage import PortletAssignmentMapping

from ely.portlets.image import imageportlet

from ely.portlets.image.tests.base import TestCase

def _test_image_file():
    """
    get test image object
    """
    here = os.path.dirname(os.path.realpath(__file__))
    path =  os.path.join(here, 'test_image.jpg')
    return file(path)

def _test_image_object():
    """
    create the image object type that the formlib field creates
    for the uploaded image.
    """
    image = Image('image', 'image', _test_image_file())
    return image

def test_assignment_data():
    data = {
        'header':u'Test Image Portlet',
        'caption':u'some kind of image',
        'image':_test_image_object(),
        'assignment_context_path':'/plone/++contextportlets++plone.rightcolumn',
        'internal_target':'front-page',
        }
    return data

class TestPortlet(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))


    def test_portlet_type_registered(self):
        portlet = getUtility(IPortletType, name='ely.portlets.image.ImagePortlet')
        self.assertEquals(portlet.addview, 'ely.portlets.image.ImagePortlet')

    def test_interfaces(self):
        portlet = imageportlet.Assignment(**test_assignment_data())
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def test_invoke_add_view(self):
        portlet = getUtility(IPortletType, name='ely.portlets.image.ImagePortlet')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)
        addview.createAndAdd(data={'image':_test_image_object()})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0], imageportlet.Assignment))

    def test_invoke_edit_view(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = imageportlet.Assignment(**test_assignment_data())
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, imageportlet.EditForm))

    def test_obtain_renderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)

        assignment = imageportlet.Assignment(**test_assignment_data())
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
        assignment = assignment or imageportlet.Assignment(**test_assignment_data())
        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)

    def test_render(self):
        renderer = self.renderer(
            context=self.portal,
            assignment=imageportlet.Assignment(**test_assignment_data()))
        renderer = renderer.__of__(self.folder)
        renderer.update()
        output = renderer.render()
        self.failUnless("<img src='http://nohost/plone/++contextportlets++plone.rightcolumn//@@image' width='200' height='260'/>" in output)
        self.failUnless('<a href="http://nohost/plone/front-page">' in output)
        self.failUnless('<span class="img-caption">some kind of image</span>' in output)
        self.failUnless('<span class="img-title">Test Image Portlet</span>' in output)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
