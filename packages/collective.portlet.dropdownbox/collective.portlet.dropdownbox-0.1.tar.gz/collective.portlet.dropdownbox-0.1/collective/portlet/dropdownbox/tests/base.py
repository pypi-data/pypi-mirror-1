from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_hasattr
from Products.CMFPlone.tests import dummy


@onsetup
def setup_product():
    """Set up additional products and ZCML required to test this product.
    
    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer.
    """
    
    # Load the ZCML configuration for this package and its dependencies
    
    fiveconfigure.debug_mode = True
    import collective.portlet.dropdownbox
    zcml.load_config('configure.zcml', collective.portlet.dropdownbox)
    fiveconfigure.debug_mode = False
    
    # We need to tell the testing framework that these products
    # should be available. This can't happen until after we have loaded
    # the ZCML.
    
    ztc.installPackage('collective.portlet.dropdownbox')

# The order here is important: We first call the deferred function and then
# let PloneTestCase install it during Plone site setup

setup_product()
ptc.setupPloneSite(products=['collective.portlet.dropdownbox'])


class TestCase(ptc.PloneTestCase):
    """Base class used for test cases
    """


    def _createType(self, context, portal_type, id, **kwargs):
        """Helper method to create a new type
        """
        ttool = getToolByName(context, 'portal_types')
        cat = self.portal.portal_catalog

        fti = ttool.getTypeInfo(portal_type)
        fti.constructInstance(context, id, **kwargs)
        obj = getattr(context.aq_inner.aq_explicit, id)

        # publish item 
        if obj and self.workflow_tool.getWorkflowsFor(obj) and self.workflow_tool.getInfoFor(obj, 'review_state') != 'published':
            self.workflow_tool.doActionFor(obj, 'publish')
            
        cat.indexObject(obj)
        return obj



    
    def setup_dummy_content(self):
        """
        We need some content for the drop down box portlet
        
        * A collection
        * A folder with mixed content - pages, folders and links
        
        portal
        ---- news
        -------- aggregator
        -------- newsitem1
        -------- newsitem2
        -------- newsitem3
        -------- newsitem4
        
        ---- folder
        -------- folder1
        -------- folder2
        -------- folder3
        -------- doc1
        -------- doc2
        -------- doc3        
        -------- image1
        -------- image2
        -------- image3        

        ---- links        
        -------- link1
        -------- link2
        -------- link3
        -------- link4
        -------- link5
        
        """
        
        # news items
        folder = self.portal.restrictedTraverse('news', default=None)
        num = 5
        while folder and num > 0:
            item_id = 'newsitem%s' % num
            if not safe_hasattr(folder, item_id):
                self._createType(folder, 'News Item', item_id, title=('News item %s' % num),)
            num -= 1
        
        # mixed content        
        if not safe_hasattr(self.portal, 'dropdownboxcontent'):
            self.portal.invokeFactory(
                'Folder', 
                'dropdownboxcontent',
                title= 'Mixed content for a drop down box',
                ) 
        folder = self.portal.restrictedTraverse('dropdownboxcontent', default=None)

        num = 3
        while folder and num > 0:
            item_id = 'folder%s' % num
            if not safe_hasattr(folder, item_id):
                self._createType(folder, 'Folder', item_id, title=('Folder %s' % num),)
            num -= 1

        num = 3
        while folder and num > 0:
            item_id = 'doc%s' % num
            if not safe_hasattr(folder, item_id):
                self._createType(folder, 'Document', item_id, title=('Document %s' % num),)
            num -= 1

        num = 3
        while folder and num > 0:
            item_id = 'image%s' % num
            if not safe_hasattr(folder, item_id):
                self._createType(folder, 'Image', item_id, title=('Image %s' % num), file=dummy.Image())
            num -= 1




        # links        
        if not safe_hasattr(self.portal, 'dropdownboxlinks'):
            self.portal.invokeFactory(
                'Folder', 
                'dropdownboxlinks',
                title= 'Links for a drop down box',
                ) 
        links = self.portal.restrictedTraverse('dropdownboxlinks', default=None)
        
        remote_urls = (
            'http://www.plone.org',
            'http://www.python.org',
            'http://www.jquery.com',
            'http://grok.zope.org',
            'http://www.zope.org',
        )
        num = 4
        while links and num >= 0:
            item_id = 'link%s' % num
            if not safe_hasattr(links, item_id):
                self._createType(links, 'Link', item_id, title=('Link %s' % num), remoteUrl= remote_urls[num])
            num -= 1









    
    def _setup(self):
        self.setRoles(('Manager',))
        ptc.PloneTestCase._setup(self)
        #self.app.REQUEST['SESSION'] = self.Session()
        self.workflow_tool = getToolByName(self.portal, 'portal_workflow')
        self.setup_dummy_content()
        self.setRoles(('Member',))

class FunctionalTestCase(ptc.FunctionalTestCase):
    """Test case class used for functional (doc-)tests
    """
