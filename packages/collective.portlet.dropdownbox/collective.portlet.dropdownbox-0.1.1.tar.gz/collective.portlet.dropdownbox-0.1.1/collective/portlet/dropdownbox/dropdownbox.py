#from zope.interface import Interface
import re
from zope.interface import implements
from zope.component import getUtility, getMultiAdapter

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from plone.i18n.normalizer.interfaces import IIDNormalizer

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.portlet.dropdownbox import DropDownBoxPortletMessageFactory as _

from Products.ATContentTypes.interface import IATTopic

from plone.app.vocabularies.catalog import SearchableTextSourceBinder

from plone.app.form.widgets.uberselectionwidget import UberMultiSelectionWidget
from plone.app.form.widgets.wysiwygwidget import WYSIWYGWidget

#from collective.portlet.dropdownbox.interfaces import ILinksBuilder

class IDropDownBoxPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """
    
    header = schema.TextLine(title=_(u"Portlet header"),
                             description=_(u"Title of the rendered portlet"),
                             required=True)
    
    targets = schema.List(
        title = _(u"Drop down box targets"),
        required = False,
        default = [],
        description=_(u"Select folder(s) or collection(s)"),
        value_type = schema.Choice(
                            __name__='target', 
                            title=u"Single target", 
                            source=SearchableTextSourceBinder({'is_folderish' : True}),
                        )
        )
    # TODO: If possible reduce the SearchableTextSourceBinder to content that has interfaces
    # IATFolder.__identifier__ or IATTopic.__identifier__

    # Note: I had expected to set the source for some interfaces / an interface
    # value_type = schema.Choice( title=u"targets", source=SearchableTextSourceBinder({'object_provides' : IATFolder.__identifier__}, default_query='path:'))
    # but that raises in plone (not the testbrowser test) :
    # UnicodeDecodeError: 'ascii' codec can't decode byte 0xc3 in position 640: ordinal not in range(128)
    # and in pdb to line 464 of zope.app.form.browser.source
    
    # and multiple interfaces didn't work well - I guess that the way I set up object_provides is wrong
    # value_type = schema.Choice( title=u"targets", source=SearchableTextSourceBinder({'object_provides' : IATFolder.__identifier__ or IATTopic.__identifier__}, default_query='path:'))

    text = schema.Text(title=_(u"Text"),
                       description=_(u"The text to render"),
                       required=False)
                       
    omit_border = schema.Bool(title=_(u"Omit portlet border"),
                              description=_(u"Tick this box if you want to render the text above without the "
                                             "standard header, border or footer."),
                              required=True,
                              default=False)
                       
    footer = schema.TextLine(title=_(u"Portlet footer"),
                             description=_(u"Text to be shown in the footer"),
                             required=False)

    more_url = schema.ASCIILine(title=_(u"Details link"),
                                  description=_(u"If given, the header and footer "
                                                  "will link to this URL."),
                                  required=False)



class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IDropDownBoxPortlet)

    header = u""
    targets = None
    text = u""
    omit_border = False
    footer = u""
    more_url = ''

    def __init__(self, header=u"", targets=None, text=u"", omit_border=False, footer=u"", more_url=''):
        self.header = header
        self.targets = targets
        self.text = text
        self.omit_border = omit_border
        self.footer = footer
        self.more_url = more_url






    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Drop down box portlet"

class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('dropdownbox.pt')

    def css_class(self):
        """Generate a CSS class from the portlet header
        """
        header = self.data.header
        normalizer = getUtility(IIDNormalizer)
        return "portlet-dropdownbox-%s" % normalizer.normalize(header)
    
    def has_link(self):
        return bool(self.data.more_url)
        
    def has_footer(self):
        return bool(self.data.footer)    
    
    def results(self):
        """
        """
        targets = self.data.targets
        if not targets:
            return None            
        
        results = []
        num=1
        for target in targets:
            obj = self.get_target(path=target)
            if obj:
                # use special adapter if target obj is a collection
                if IATTopic.providedBy(obj):
                    links_helper = getMultiAdapter((self.context, self.request), name=u'dropdownbox_collection_links_helper')
                else:
                    links_helper = getMultiAdapter((self.context, self.request), name=u'dropdownbox_links_helper')            
                # or do links_helper = getMultiAdapter((self.context, self.request), ILinksBuilder) 
                # or do links_helper = ILinksBuilder(self.context) - had some problems with this one keep raising lookuperrors 
                # depending on have the adapter is confgured in the configure.zcml
                dic = {
                    # we need a uniquie ide for the ...
                    'id': '%s-form-%s' % (self.css_class(), num),
                    'title': obj.Title(),
                    'description': obj.Description(),
                    'links': links_helper.links(obj),
                }
                num += 1
                results.append(dic)        
        return results
    
    
    def get_target(self, path=None):
        """ get the collection or the folder which the portlet is pointing to"""

        if not path:
            return None

        if path.startswith('/'):
            path = path[1:]
        
        if not path:
            return None

        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        portal = portal_state.portal()
        return portal.restrictedTraverse(path, default=None)
    
    
    def has_text(self):
        """Is the text field really empty ? kupu sometimes leaves som
            markup behind the scene - so lets get the text striped for
            markup and white spaces before and after the text this
            approach requires a regular expression.
           
           TODO: clear out -- is this a sane approach ? is a reg expression expensive due to performance ?
        """
        text = self.data.text
        return text and len(re.sub('<(?!(?:a\s|/a|!))[^>]*>','',text).replace("\n", "").strip())
    

    def redirect_to(self):
        """
        Redirects to a destination path
        or url given in a (selection) form. In this case we mostely 
        gets http://... urls...
        
        Based on an old plone help center script.
        
        Its needed to get the form to work with out java script. 
        There can be multiple forms for that reason some work arounds is needed
        to get the selection id from the request.
        
        TODO: / NICETOHAVE:
        Another approach could be to have it on the form only like the new 
        plone help center does - have a look at -->
        http://plone.org/documentation/tutorial/testing/writing-a-plonetestcase-unit-integration-test?%3Aaction=types-of-tests#
        
        I tried it out in the template 
            <form action="#"
                  method="get"
                  tal:condition="nothing">...........
                <select onchange="window.location.href=this.options[this.selectedIndex].value"
                        id="destination" name=":action"
                        tal:attributes="id item/id;">.........
        Its the :action that is of interest but it seems for me only to work
        on relativ urls with out http:/
        
        Works:
        http://www.plone.local:8080/dummy/sektionsside?%3Aaction=folder-1#
        
        Dont work: 
        http://www.plone.local:8080/dummy/sektionsside?%3Aaction=http%3A%2F%2Fwww.plone.local%3A8080%2Fnyheder%2Fnyhed-5#
        
        
        
        
        """
        request = self.request
        context = self.context
        
        destination = None
        for item in self.results():
            if request.has_key(item['id']):
                destination = request.get(item['id'])

        if not destination or not len(destination) > 0:
            back_url = request.get('URL1', request.get('URL2'))
            return back_url

        if destination.startswith('http://'):
            return request.response.redirect(destination)
        else:
            return request.response.redirect('%s/%s' % (context.absolute_url(),
                                                            destination))


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IDropDownBoxPortlet)
    form_fields['text'].custom_widget = WYSIWYGWidget
    form_fields['targets'].custom_widget = UberMultiSelectionWidget
    
    label = _(u"Add Drop down box portlet")
    description = _(u"This portlet ...")

    def create(self, data):
        return Assignment(**data)
        

class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IDropDownBoxPortlet)
    form_fields['text'].custom_widget = WYSIWYGWidget
    form_fields['targets'].custom_widget = UberMultiSelectionWidget
    
    label = _(u"Edit Drop down box portlet")
    description = _(u"This portlet ...")
