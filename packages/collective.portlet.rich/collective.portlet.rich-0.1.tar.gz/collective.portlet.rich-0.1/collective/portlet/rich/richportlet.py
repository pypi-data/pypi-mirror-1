import re

from plone.app.form.widgets.wysiwygwidget import WYSIWYGWidget
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from plone.app.portlets.portlets import base
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.portlets.interfaces import IPortletDataProvider

from zope import schema
from zope.component import getUtility, getMultiAdapter
from zope.formlib import form
from zope.interface import implements

from Products.ATContentTypes.interface import IATImage
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.portlet.rich import RichPortletMessageFactory as _


class IRichPortlet(IPortletDataProvider):
    """A portlet which renders predefined static HTML.

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    target_header_image = schema.Choice(title=_(u"Portlet header image"),
                                  description=_(u"Find the image"),
                                  required=False,
                                  source=SearchableTextSourceBinder({'object_provides' : IATImage.__identifier__}))

    header = schema.TextLine(title=_(u"Portlet header"),
                             description=_(u"Title of the rendered portlet"),
                             required=True)

    header_more_url = schema.ASCIILine(title=_(u"Portlet header details link"),
                                  description=_(u"If given, the header "
                                                  "will link to this URL."),
                                  required=False)

    text = schema.Text(title=_(u"Text"),
                       description=_(u"The text to render"),
                       required=False)                       
                       
    links = schema.List(
        title=_(u"Links"),
        description=_(u"Write up a link like this 'http://www.plone.org:Title:Description'. "
                    "Internal link should be specified as '/my-site/my-page'. The "
                    "title and description is optional, for example 'http://www.plone.org:Title:'. "
                    "Description is used as the "
                    "title attribute of the link tag."),
        required=False,
        value_type = schema.TextLine(),
    )
    
    # vocabulary: is just set by name of the wanted vocabulary (the name specified in the configure.zcml)
    # TODO: how to specify a default / selected vacobulary. I had expected something like:
    # default=''
    links_css = schema.Choice(title=_(u"Links styles"),
                              description=_(u"Choose a css style for the links list."),
                              required=True,
                              vocabulary='collective.portlet.rich.vocabularies.LinksCSSVocabulary',
                              )
    
    omit_border = schema.Bool(title=_(u"Omit portlet border"),
                              description=_(u"Tick this box if you want to render the text above without the "
                                             "standard header, border or footer."),
                              required=True,
                              default=False)
                       
    footer = schema.TextLine(title=_(u"Portlet footer"),
                             description=_(u"Text to be shown in the footer"),
                             required=False)

    footer_more_url = schema.ASCIILine(title=_(u"Portlet footer details link"),
                                  description=_(u"If given, the footer "
                                                  "will link to this URL."),
                                  required=False)


class Assignment(base.Assignment):
    """Portlet assignment.
    
    This is what is actually managed through the portlets UI and associated
    with columns.
    """
    
    implements(IRichPortlet)

    target_header_image = None
    header = u""
    header_more_url = ''
    text = u""
    links = []
    #Dont use the token here
    links_css = 'links_list'
    omit_border = False
    footer = u""
    footer_more_url = ''

    def __init__(self, target_header_image=None, header=u"", header_more_url='', text=u"", links = [], links_css = 'links_list', omit_border=False, footer=u"", footer_more_url=''):
        self.target_header_image = target_header_image
        self.header = header
        self.header_more_url = header_more_url
        self.text = text
        self.links = links
        self.links_css = links_css
        self.omit_border = omit_border
        self.footer = footer
        self.footer_more_url = footer_more_url


    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen. Here, we use the title that the user gave.
        """
        return self.header    
    
    
class Renderer(base.Renderer):
    """Portlet renderer.
    
    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('richportlet.pt')

    # also taken from collection portlet 
    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        self.portal_url = portal_state.portal_url()
        self.portal = portal_state.portal()
    
    def css_class(self):
        """Generate a CSS class from the portlet header
        """
        header = self.data.header
        normalizer = getUtility(IIDNormalizer)
        return "portlet-richportlet-%s" % normalizer.normalize(header)
    
    def has_header_link(self):
        return bool(self.data.header_more_url)

    def has_text(self):
        """Is the text field really empty ? kupu do some times leave som
            markup behind the scene - so lets get the text 
           striped for markup and white spaces before and after the text
           this approach requires a regular expression. 
           
           TODO: clear out -- is this a sane approach ? is a reg expression expensive due to performance ?
        """
        text = self.data.text
        return text and len(re.sub('<(?!(?:a\s|/a|!))[^>]*>','',text).replace("\n", "").strip())
    
    def has_footer_link(self):
        return bool(self.data.footer_more_url)

    def has_footer(self):
        return bool(self.data.footer)

    # @memoize
    def list_links(self):
        """ 
        Return a list of links as dictionaries.
        """
        links = self.data.links
        result = []
        for link in links:
            link_list = link.split(':')
            dic = {
                'title': None,
                'description': None,
                'url': None,
            }
            # build the link - it might be an internal link starting with '/'
            # we dont want to get to specific about looking for http:// it might
            # be mailto: https:// etc...
            if not link.startswith('/') and link_list[0] and link_list[1]:
                dic['url'] ="%s:%s" % (link_list[0], link_list[1])
            elif link.startswith('/'):
                dic['url'] ="%s%s" % (self.portal_url, link_list[0])                
            else:
                break
            #build the title (is optional)
            if len(link_list[-2]):
                dic['title'] = link_list[-2]
            else: 
                dic['title'] = dic['url']
            #build the description (is optional)
            if len(link_list[-1]):
                dic['description'] = link_list[-1]
            result.append(dic)
        return result



    # @memoize
    def get_header_image_tag(self):
        """ 
        get the image the portlet is pointing to
        taken from the collection portlet:
        https://svn.plone.org/svn/plone/plone.portlet.collection/trunk/plone/portlet/collection/collection.py

        some naive obervations:
        target_header_image uses the uberselecton widget and do not return and object like
        the archetypes reference field.

        """
        
        image_path = self.data.target_header_image
        
        
        # it feels insane that i need to do manual strippping of the first slash in this string.
        # I must be doing something wrong
        # please make this bit more sane
        
        if image_path is None or len(image_path)==0:
            return None
        # The portal root is never a image
        
        if image_path[0]=='/':
            image_path = image_path[1:]
        image = self.portal.restrictedTraverse(image_path, default=None)
        
        # we should also check that the returned object implements the interfaces for image
        # So that we don't accidentally return folders and stuff that will make things break
        if IATImage.providedBy(image) and image.getImage() is not None:
            return image.tag(scale='mini',)
        else:
            return None




        

class AddForm(base.AddForm):
    """Portlet add form.
    
    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IRichPortlet)
    form_fields['text'].custom_widget = WYSIWYGWidget
    form_fields['target_header_image'].custom_widget = UberSelectionWidget
    
    label = _(u"Add Rich Portlet")
    description = _(u"This portlet ...")

    def create(self, data):
        return Assignment(**data)




class EditForm(base.EditForm):
    """Portlet edit form.
    
    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IRichPortlet)
    form_fields['text'].custom_widget = WYSIWYGWidget
    form_fields['target_header_image'].custom_widget = UberSelectionWidget
    
    label = _(u"Edit Rich Portlet")
    description = _(u"This portlet ...")
    
