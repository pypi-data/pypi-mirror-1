from zope.interface import Interface

from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.portlet.paypal import PayPalPortletMessageFactory as _

class IPayPalPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    # TODO: Add any zope.schema fields here to capture portlet configuration
    # information. Alternatively, if there are no settings, leave this as an
    # empty interface - see also notes around the add form and edit form 
    # below.

    donation_title = schema.TextLine(title=_(u"Portlet Title"),
                                 description=_(u"The text that will appear above the portlet on your Plone website (e.g. Donations)."),
                                 required=True)

    donation_acct = schema.TextLine(title=_(u"PayPal Account Name"),
                                 description=_(u"The PayPal account that you want donations sent to."),
                                 required=True)

    donation_code = schema.TextLine(title=_(u"Currency Code"),
                                 description=_(u"The currency code for the donations (e.g. USD, EUR, GBP)."),
                                 required=True)

    donation_amts = schema.Tuple(title=_(u'Possible Donation Amounts'),
                                 description=_(u'You can configure possible donation amounts for the portlet.  These will appear in a dropdown box above the donate button.'),
                                 default=(10.00, 25.00, 50.00, 75.00, 100.00,),
                                 required=True,
                                 value_type=schema.Float(title=u"Amount"))

    donation_other = schema.Bool(title=_(u'Enable "Other" Option'),
                                 description=_(u'If you check this box, an "Other" option will appear in the amounts box.  If the user clicks on this option, they will be able to input a custom amount to donate.'),
                                 default=True,
                                 required=False)

class Assignment(base.Assignment):
    """Portlet assignment.
    
    This is what is actually managed through the portlets UI and associated
    with columns.
    """
    
    implements(IPayPalPortlet)

    # TODO: Set default values for the configurable parameters here

    donation_title = u""
    donation_acct = u"Donations"
    donation_code = u"USD"
    donation_amts = (10.00, 25.00, 50.00, 75.00, 100.00,)
    donation_other = True

    # TODO: Add keyword parameters for configurable parameters here

    def __init__(self, donation_title=u"Donations", donation_acct=u"", donation_code=u"", donation_amts=(10.00, 25.00, 50.00, 75.00, 100.00,), donation_other=True):
        self.donation_title = donation_title
        self.donation_acct = donation_acct
	self.donation_code = donation_code
	self.donation_amts = donation_amts
	self.donation_other = donation_other
        
    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "PayPal portlet"

class Renderer(base.Renderer):
    """Portlet renderer.
    
    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('paypalportlet.pt')
        
# NOTE: If this portlet does not have any configurable parameters, you can
# inherit from NullAddForm and remove the form_fields variable.

class AddForm(base.AddForm):
    """Portlet add form.
    
    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IPayPalPortlet)

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
    form_fields = form.Fields(IPayPalPortlet)
