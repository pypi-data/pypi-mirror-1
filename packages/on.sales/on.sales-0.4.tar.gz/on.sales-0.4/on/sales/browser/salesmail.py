""" Mailform to send to salespersons"""

import re

from zope.interface import Interface

from zope import schema

from zope.formlib import form
from Products.Five.formlib import formbase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.statusmessages.interfaces import IStatusMessage

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName

from on.sales.salesarea import mailaddresses
from on.sales import OnSalesMessageFactory as _

""" Define a valiation method for email addresses
    taken from optilux-code
"""
class NotAnEmailAddress(schema.ValidationError):
    __doc__ = _(u"Invalid email address")

check_email = re.compile(r"[a-zA-Z0-9._%-]+@([a-zA-Z0-9-]+\.)*[a-zA-Z]{2,4}").match
def validate_email(value):
    if not check_email(value):
        raise NotAnEmailAddress(value)
    return True

MESSAGE_TEMPLATE = """\
Nachricht von: %(name)s <%(email_address)s>
Telefon: %(phone)s

%(message)s
"""

class IMailForm(Interface):
    """Define the fields of our form
    """
    
    subject = schema.TextLine(title=_(u"Subject"),
                              required=True)
                              
    name = schema.TextLine(title=_(u"Your name"),
                              required=True)
    
    email_address = schema.ASCIILine(title=_(u"Your Email Address"),
                                    description=_(u"We will use this to contact you if you request it"),
                                    required=True,
                                    constraint=validate_email)
    
    phone = schema.ASCIILine(title=_(u"Your Phone Number"),
                                    description=_(u"We will use this to contact you if you request it"),
                                    required=False)
    
    message = schema.Text(title=_(u"Message"),
                          description=_(u"Please keep to 1,000 characters"),
                          required=True,
                          max_length=1000)

class MailForm(formbase.PageForm):
    form_fields = form.FormFields(IMailForm)
    label = _(u"Send an Email to our Sales Organization")
    description = _(u"If you want to be contacted by our sales people, please leave us a note using the form below! We will will get it even if there is no sales agent assigned to your area.")
    
    # This trick hides the editable border and tabs in Plone
    def __call__(self):
        self.request.set('disable_border', True)
        return super(MailForm, self).__call__()
    
    @form.action(_(u"Send"))
    def action_send(self, action, data):
        """Send the email to every Sales agent responsible for the
        current sales area and redirect to the front page, showing a
        status message to say the message was received.
        """
        
        context = self.context
        
        mailhost = getToolByName(context, 'MailHost')
        urltool = getToolByName(context, 'portal_url')
        
        portal = urltool.getPortalObject()

        # Construct and send a message
        to_address = mailaddresses(context)
        source = "%s <%s>" % (data['name'], data['email_address'])
        subject = data['subject']
        message = MESSAGE_TEMPLATE % data 
        
        for address in to_address:
            mailhost.secureSend(message,
                                address,
                                str(source),
                                subject=subject,
                                subtype='plain',
                                debug=False,
                                From=source)
        
        # Issue a status message
        confirm = _(u"Thank you! Your message has been received and we will respond as soon as possible")
        IStatusMessage(self.request).addStatusMessage(confirm, type='info')
        
        # Redirect to the portal front page. Return an empty string as the
        # page body - we are redirecting anyway!
        self.request.response.redirect(portal.absolute_url())
        return ''
			  
