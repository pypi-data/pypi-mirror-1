from zope.component import getUtility, getMultiAdapter

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.storage import PortletAssignmentMapping

from collective.portlet.dropdownbox import dropdownbox

from collective.portlet.dropdownbox.tests.base import TestCase

from zope.annotation.interfaces import IAttributeAnnotatable
from zope.interface import classImplements
from zope.publisher.browser import TestRequest

class TestPortlet(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))

    def test_portlet_type_registered(self):
        portlet = getUtility(IPortletType, name='collective.portlet.dropdownbox.DropDownBoxPortlet')
        self.assertEquals(portlet.addview, 'collective.portlet.dropdownbox.DropDownBoxPortlet')

    def test_interfaces(self):
        # TODO: Pass any keyword arguments to the Assignment constructor
        portlet = dropdownbox.Assignment()
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def test_invoke_add_view(self):
        portlet = getUtility(IPortletType, name='collective.portlet.dropdownbox.DropDownBoxPortlet')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        # TODO: Pass a dictionary containing dummy form inputs from the add form
        addview.createAndAdd(data={})

        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0], dropdownbox.Assignment))

    # NOTE: This test can be removed if the portlet has no edit form
    def test_invoke_edit_view(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = dropdownbox.Assignment()
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, dropdownbox.EditForm))

    def test_obtain_renderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)

        # TODO: Pass any keyword arguments to the Assignment constructor
        assignment = dropdownbox.Assignment()

        renderer = getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, dropdownbox.Renderer))

class TestRenderer(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))
        
        
        # setup a request - needed for the redirect_to() of the dropdownbox portlet
        request_environment = {
            'destination': '',
            'URL0':'http://nohost/plone/Members/test_user_1_',
            'URL1':'http://nohost/plone/Members/test_user_1_',
            'URL2':'http://nohost/plone/Members',
        }
        # NOTE: based on the doc test in plone.portlets -
        # for our memoised views to work, we need to make the request annotatable
        classImplements(TestRequest, IAttributeAnnotatable)
        self.request = TestRequest(environ=request_environment)        
        
        # TODO: perhaps ^^^move to the TestCase it self


    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)

        # TODO: Pass any default keyword arguments to the Assignment constructor
        assignment = assignment or dropdownbox.Assignment()
        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)


    def test_render(self):
        r = self.renderer(
                    context=self.portal, 
                    request=self.request,
                    assignment=dropdownbox.Assignment(header=u"title", text="<b>text</b>")
                )
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        self.failUnless('title' in output)
        self.failUnless('<b>text</b>' in output)


    def test_css_class(self):
        r = self.renderer(
                    context=self.portal, 
                    request=self.request,
                    assignment=dropdownbox.Assignment(header=u"Welcome text", text="<b>text</b>")
                )
        self.assertEquals('portlet-dropdownbox-welcome-text', r.css_class())


    def test_dropdownbox_links(self):
        
        # the render depends on some content set up - lets do some basic checks
        self.failUnless(self.portal.news.aggregator.queryCatalog())
        folder = self.portal.restrictedTraverse('dropdownboxcontent', default=None)
        self.failUnless(folder)
        self.failUnless(folder.contentIds())        
        folder = self.portal.restrictedTraverse('dropdownboxlinks', default=None)
        self.failUnless(folder)
        self.failUnless(folder.contentIds())        
        
        # Keep on testing the renderer
        
        # Target paths should NOT be u'/whateverPathwanted/item', 
        # that will result in the restrictedTraverse() lookup to be none
        r = self.renderer(
                    context=self.portal, 
                    request=self.request,
                    assignment=dropdownbox.Assignment(
                                                header=u"Short cuts", 
                                                targets=['/news/aggregator', '/dropdownboxcontent', '/dropdownboxlinks'],
                                                text="<b>Lots of funny rich text</b>",
                                                omit_border = False,
                                                footer = u"Portlet footer text",
                                                more_url = 'http://www.plone.org',
                                            ),
                )
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        # print output
        self.failUnless('<option value="http://nohost/plone/news/newsitem3">News item 3</option>' in output)        
        self.failUnless('<option value="http://nohost/plone/dropdownboxcontent/folder1">Folder 1</option>' in output)        
        self.failUnless('<option value="http://nohost/plone/dropdownboxcontent/image2/view">Image 2</option>' in output)        
        self.failUnless('<option value="http://www.plone.org">Link 0</option>' in output)        
        self.failUnless('Portlet footer text' in output)         
        self.failUnless('<a href="http://www.plone.org">Portlet footer text</a>' in output)                 


    def test_dropdownbox_links_omit_border(self):
        r = self.renderer(
                    context=self.portal, 
                    request=self.request,
                    assignment=dropdownbox.Assignment(
                                                header=u"Short cuts", 
                                                targets=['/news/aggregator', '/dropdownboxcontent', '/dropdownboxlinks'],
                                                text="<b>Lots of funny rich text</b>",
                                                omit_border=True,
                                                footer = u"Portlet footer text",
                                                more_url = 'http://www.plone.org',
                                            ),
                )
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        # print output
        self.failIf('Short cuts' in output)        
        self.failUnless('<option value="http://nohost/plone/news/newsitem3">News item 3</option>' in output)        
        self.failUnless('<option value="http://nohost/plone/dropdownboxcontent/folder1">Folder 1</option>' in output)        
        self.failUnless('<option value="http://nohost/plone/dropdownboxcontent/image2/view">Image 2</option>' in output)        
        self.failUnless('<option value="http://www.plone.org">Link 0</option>' in output)        
        self.failIf('Portlet footer text' in output)         
        self.failIf('<a href="http://www.plone.org">Portlet footer text</a>' in output)                 


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
