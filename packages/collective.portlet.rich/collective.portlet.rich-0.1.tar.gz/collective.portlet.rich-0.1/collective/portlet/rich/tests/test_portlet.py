from zope.component import getUtility, getMultiAdapter

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from Products.CMFPlone.tests import dummy

from plone.app.portlets.storage import PortletAssignmentMapping

from collective.portlet.rich import richportlet

from collective.portlet.rich.tests.base import TestCase

class TestPortlet(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))

    def testPortletTypeRegistered(self):
        portlet = getUtility(IPortletType, name='collective.portlet.rich.RichPortlet')
        self.assertEquals(portlet.addview, 'collective.portlet.rich.RichPortlet')

    def testInterfaces(self):
        portlet = richportlet.Assignment(header=u"title", text="text")
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def testInvokeAddview(self):
        portlet = getUtility(IPortletType, name='collective.portlet.rich.RichPortlet')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)
        
        #TODO: clean the dummy.Image() up
        data = {
            'target_header_image' : dummy.Image(), 
            'header' : u"test title", 
            'text' : u"test text", 
            'links' : [u'http://www.plone.org:Link title 1:Link description 1', u'http://www.python.org:Link title 2:Link description 2'],
        }
        addview.createAndAdd(data=data)
        
        self.assertEquals(len(mapping), 1)
        self.failUnless(isinstance(mapping.values()[0], richportlet.Assignment))

    def testInvokeEditView(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping['foo'] = richportlet.Assignment(header=u"rich portlet header", text="rich portlet text")
        editview = getMultiAdapter((mapping['foo'], request), name='edit')
        self.failUnless(isinstance(editview, richportlet.EditForm))

    def testRenderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = richportlet.Assignment(header=u"rich portlet header", text="rich portlet text")

        renderer = getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, richportlet.Renderer))

class TestRenderer(TestCase):
    
    def afterSetUp(self):
        self.setRoles(('Manager',))

    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)
        assignment = assignment or richportlet.Assignment(header=u"rich portlet header", text="rich portlet text")

        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)

    def test_render(self):
        r = self.renderer(context=self.portal, assignment=richportlet.Assignment(header=u"rich portlet header", text="<b>rich portlet text</b>"))
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        # print output
        self.failUnless('rich portlet header' in output)
        self.failUnless('<b>rich portlet text</b>' in output)
        
        
    def test_render_has_header_link(self):
        r = self.renderer(context=self.portal, assignment=richportlet.Assignment(header=u"rich portlet header", header_more_url="http://www.plone.org", text="<b>rich portlet text</b>"))
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        # print output
        self.failUnless('<a href="http://www.plone.org">rich portlet header</a>' in output)
        self.failUnless('<b>rich portlet text</b>' in output)
        
    def test_render_has_footer_link(self):
        r = self.renderer(context=self.portal, assignment=richportlet.Assignment(header=u"rich portlet header", text="<b>rich portlet text</b>", footer=u"rich portlet footer", footer_more_url="http://www.plone.org"))
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        # print output
        self.failUnless('rich portlet header' in output)
        self.failIf('<a href="http://www.plone.org">rich portlet header</a>' in output)
        self.failUnless('<b>rich portlet text</b>' in output)
        self.failUnless('<a href="http://www.plone.org">rich portlet footer</a>' in output)
    
    def test_render_get_header_image_tag(self):
        self.folder.invokeFactory('Image', id='image')
        target_header_image = '/Members/test_user_1_/image'
        r = self.renderer(context=self.portal, assignment=richportlet.Assignment(target_header_image=target_header_image, header=u"rich portlet header", text="<b>rich portlet text</b>",))
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        # print output
        image_tag = '<img src="http://nohost/plone/Members/test_user_1_/image/image_mini" alt="" title="" height="0" width="0" />'
        self.failUnless(image_tag in output)


    def test_render_list_links(self):
        links = [u'http://www.plone.org:Link title 1:Link description 1', u'http://www.python.org:Link title 2:Link description 2',]
        r = self.renderer(context=self.portal, assignment=richportlet.Assignment(header=u"rich portlet header", text="<b>rich portlet text</b>", links = links,))
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        # print output
        self.failUnless('href="http://www.plone.org"' in output)
        self.failUnless('title="Link description 1">Link title 1' in output)

    def test_render_list_links_internal(self):
        links = [u'/front-page:Internal link title 1:Internal link description 1', u'/news:Internal link title 2:Internal link description 2',]
        r = self.renderer(context=self.portal, assignment=richportlet.Assignment(header=u"rich portlet header", text="<b>rich portlet text</b>", links = links,))
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        # print output
        self.failUnless('href="http://nohost/plone/front-page' in output)
        self.failUnless('title="Internal link description 1">Internal link title 1' in output)

    def test_render_list_links_css_style(self):
        links = [u'http://www.plone.org:Link title 1:Link description 1', u'http://www.python.org:Link title 2:Link description 2',]
        links_css = 'links_list_description'
        r = self.renderer(context=self.portal, assignment=richportlet.Assignment(header=u"rich portlet header", text="<b>rich portlet text</b>", links = links, links_css=links_css,))
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        # print output
        self.failUnless('href="http://www.plone.org"' in output)
        self.failUnless('title="Link description 1">Link title 1' in output)

    def test_render_has_text_only_html_tags(self):
        
        html_tags_no_text = "  \n\n         <p><br %><b></b></p>    \n  \n    <br />          "
        r = self.renderer(context=self.portal, assignment=richportlet.Assignment(header=u"rich portlet header", header_more_url="http://www.plone.org", text=html_tags_no_text))
        r = r.__of__(self.folder)
        r.update()
        output = r.render()
        # print output
        self.failIf(html_tags_no_text in output)


    def test_css_class(self):
        r = self.renderer(context=self.portal, 
                          assignment=richportlet.Assignment(header=u"Rich portlet header", text="<b>rich portlet text</b>"))
        self.assertEquals('portlet-richportlet-rich-portlet-header', r.css_class())

        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
