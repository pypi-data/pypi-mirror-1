from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from medialog.portlet.donate import DonatePortletMessageFactory as _

class IDonatePortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    # TODO: Add any zope.schema fields here to capture portlet configuration
    # information. Alternatively, if there are no settings, leave this as an
    # empty interface - see also notes around the add form and edit form
    # below.

    paypaltext = schema.TextLine(title=_(u"Name"),
                             description=_(u"Write in your organisation name"),
                             required=True)
    
    paypalmail = schema.TextLine(title=_(u"E-mail (on paypal)"),
                             description=_(u"Write in your e-mail"),
                             required=True)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IDonatePortlet)

    paypaltext = u''
    paypalmail = u''

    def __init__(self, paypaltext=None):
        self.paypaltext = paypaltext
        

    def __init__(self, paypalmail=None):
        self.paypalmail = paypalmail

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Donate Portlet"

class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('donateportlet.pt')

class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IDonatePortlet)

    def create(self, data):
        return Assignment(**data)

class AddForm(base.AddForm):
    form_fields = form.Fields(IDonatePortlet)
    form_fields['paypaltext']
    
    def create(self, data):
        return Assignment(paypaltext=data.get('paypaltext', u""))
        
    form_fields['paypalmail']
    def create(self, data):
        return Assignment(paypaltext=data.get('paypalmail', u""))
    
  

# NOTE: If this portlet does not have any configurable parameters, you
# can use the next AddForm implementation instead of the previous.

# class AddForm(base.NullAddForm):
#     """Portlet add form.
#     """
#     def create(self):
#         return Assignment()

# NOTE: If this portlet does not have any configurable parameters, you
# can remove the EditForm class definition and delete the editview
# attribute from the <plone:portlet /> registration in configure.zcml

class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IDonatePortlet)
    form_fields['paypaltext'] 
    form_fields['paypalmail'] 