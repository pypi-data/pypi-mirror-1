from zope.interface import Interface

from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.portlet.amazon import AmazonPortletMessageFactory as _

class IAmazonPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    # TODO: Add any zope.schema fields here to capture portlet configuration
    # information. Alternatively, if there are no settings, leave this as an
    # empty interface - see also notes around the add form and edit form 
    # below.

    amazon_title = schema.TextLine(title=_(u"Portlet Title"),
                                 description=_(u"The title displayed at the top of the portlet."),
                                 required=True)

    amazon_track = schema.TextLine(title=_(u"Amazon Affiliates Tracker ID"),
                                 description=_(u"This is the tracker ID from your Amazon Affiliates account that you want to use with this portlet to collect money."),
                                 required=True)

    amazon_asin = schema.TextLine(title=_(u"Product ASIN"),
                                 description=_(u"This is the ASIN (Amazon Standard Identification Number) of the product that you want to display.  If the product has an ISBN, you can put this here."),
                                 required=False)

    amazon_bgclr = schema.TextLine(title=_(u"Portlet Background Color"),
                                 description=_(u"This is the 6-character HTML color code representing the background color of the portlet."),
                                 required=True)

    amazon_txclr = schema.TextLine(title=_(u"Portlet Text Color"),
                                 description=_(u"This is the 6-character HTML color code representing the text color of the portlet."),
                                 required=True)

    amazon_lkclr = schema.TextLine(title=_(u"Portlet Hyperlink Color"),
                                 description=_(u"This is the 6-character HTML color code representing the hyperlink color of the portlet."),
                                 required=True)

class Assignment(base.Assignment):
    """Portlet assignment.
    
    This is what is actually managed through the portlets UI and associated
    with columns.
    """
    
    implements(IAmazonPortlet)

    # TODO: Set default values for the configurable parameters here

    amazon_title = u"A Book You Might Like"
    amazon_track = u""
    amazon_asin = u""
    amazon_bgclr = u""
    amazon_txclr = u""
    amazon_lkclr = u""

    # TODO: Add keyword parameters for configurable parameters here

    def __init__(self, amazon_title=u"", amazon_track=u"", amazon_asin="", amazon_bgclr=u"", amazon_txclr=u"", amazon_lkclr=u""):
       self.amazon_title = amazon_title
       self.amazon_track = amazon_track
       self.amazon_asin = amazon_asin
       self.amazon_bgclr = amazon_bgclr
       self.amazon_txclr = amazon_txclr
       self.amazon_lkclr = amazon_lkclr
        
    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Amazon portlet"

class Renderer(base.Renderer):
    """Portlet renderer.
    
    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('amazonportlet.pt')

    def has_asin(self):
        return bool(self.data.amazon_asin)

# NOTE: If this portlet does not have any configurable parameters, you can
# inherit from NullAddForm and remove the form_fields variable.

class AddForm(base.AddForm):
    """Portlet add form.
    
    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IAmazonPortlet)

    def create(self, data):
        return Assignment(**data)

# NOTE: IF this portlet does not have any configurable parameters, you can
# remove this class definition and delete the editview attribute from the
# <plone:portlet /> registration in configure.zcml

class EditForm(base.EditForm):
    """Portlet edit form.
    
    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IAmazonPortlet)
