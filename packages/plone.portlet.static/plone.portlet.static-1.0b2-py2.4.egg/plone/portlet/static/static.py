from zope.interface import Interface

from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.portlet.static import StaticMessageFactory as _

class IStaticPortlet(IPortletDataProvider):
    """A portlet which renders predefined static HTML.

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    header = schema.TextLine(title=_(u"Portlet header"),
                             description=_(u"Title of the rendered portlet"),
                             required=True)

    header_url = schema.ASCIILine(title=_(u"Header URL"),
                                  description=_(u"If specified, the portlet header "
                                                 "will turn into a link."),
                                  required=False)

    text = schema.Text(title=_(u"Text"),
                       description=_(u"The text to render"),
                       required=True)
                       
    footer = schema.TextLine(title=_(u"Portlet footer"),
                             description=_(u"Text to be shown in the footer"),
                             required=False)

    footer_url = schema.ASCIILine(title=_(u"Footer URL"),
                                  description=_(u"If specified, the portlet footer "
                                                 "will turn into a link."),
                                  required=False)

class Assignment(base.Assignment):
    """Portlet assignment.
    
    This is what is actually managed through the portlets UI and associated
    with columns.
    """
    
    implements(IStaticPortlet)

    header = u""
    header_url = ''
    text = u""
    footer = u""
    footer_url = ''

    def __init__(self, header=u"", header_url='', text=u"",
                  footer=u"", footer_url=''):
        self.header = header
        self.header_url = header_url
        self.text = text
        self.footer = footer
        self.footer_url = footer_url
        
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

    render = ViewPageTemplateFile('static.pt')
    
    def header_is_link(self):
        return bool(self.data.header_url)
        
    def has_footer(self):
        return bool(self.data.footer)
        
    def footer_is_link(self):
        return bool(self.data.footer_url)

class AddForm(base.AddForm):
    """Portlet add form.
    
    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IStaticPortlet)

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    """Portlet edit form.
    
    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IStaticPortlet)