import re

from zope.interface import Interface, implements
from zope import schema
from zope.formlib import form
from zope.schema.interfaces import ValidationError

from Products.Five.formlib import formbase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

from collective.salesforce.rsvp import RSVPMessageFactory as _

class IRegistrationForm(Interface):
    """Interface for registration form
    """

class InvalidEmailAddress(schema.ValidationError):
    __doc__ = _(u"Invalid email address")

check_email = re.compile(r"[a-zA-Z0-9._%-]+@([a-zA-Z0-9-]+\.)*[a-zA-Z]{2,4}").match
def validate_email(value):
    if not check_email(value):
        raise InvalidEmailAddress(value)
    return True


class IRegistrationFormFields(Interface):
    """Fields needed for a form for registration
    """
    first_name = schema.TextLine(
            title = _(u"First Name"),
            description = _(u"Your first name"),
            required=True,
    )
    
    last_name = schema.TextLine(
            title = _(u"Last Name"),
            description = _(u"Your last name"),
            required=True,
    )
    
    email = schema.ASCIILine(
            title = _(u"Email"),
            description = _(u"Your email address"),
            required=True,
            constraint=validate_email,
    )
    
    company = schema.TextLine(
            title = _(u"Organization"),
            description = _(u"Your organization name"),
            required=False,
    )
    
    phone = schema.TextLine(
            title = _(u"Phone"),
            description = _(u"Your preferred phone number"),
            required=False,
    )

def is_still_rsvpable(form, action, data):
    """Confirm that there's still capacity or waitlist
       accepting status for the RSVPable item, which may
       not have been the case when the form was 
       initially loaded.
    """
    from collective.salesforce.rsvp.browser import registration
    errors = []
    registration_viewlet = registration.RegistrationViewlet(form.context, form.request, 
                                               u'rsvp.register', u'plone.belowcontentbody')
    
    if not registration_viewlet.isUnderCapacity() \
       and not registration_viewlet.isWaitlistable():
        # looks like we presented the form to the user, but
        # have since become overbooked.  We raise a validation
        # error and place a flag for failure handling within data
        data['over-capacity-failure'] = True
        errors.append(ValidationError)
        return errors

class RegistrationForm(formbase.Form):
    """The formlib class for the next edition date config page
    """
    implements(IRegistrationForm)
    
    form_fields = form.Fields(IRegistrationFormFields)
    
    template = ViewPageTemplateFile('templates/registration-form.pt')
    
    status = errors = None
    prefix = 'form'
    
    @form.action(_(u"register"), validator=is_still_rsvpable, failure='handle_register_action_failure')
    def action_register(self, action, data):
        lead_obj = dict(type='Lead',
            FirstName = data['first_name'],
            LastName = data['last_name'],
            Email = data['email'],
            Phone = data.has_key('phone') and data['phone'] or '',
            Company = data.has_key('company') and data['company'] or _(u"[not provided]"),  # and some required fields...
            LeadSource = _(u"Website RSVP"),                                                # ...for the lead object
        )
        
        sbc = getToolByName(self.context, 'portal_salesforcebaseconnector')
        lead_res = sbc.create(lead_obj)
        
        signupSFObjectId = self.context.getField('sfObjectId').get(self.context)
        if signupSFObjectId:
            # practically speaking, the user won't ever make it here
            # but we confirm that there is a set sfObjectId on the
            # rsvpable object to be safe
            junction_obj = dict(type='CampaignMember',
                LeadId = lead_res[0]['id'],
                CampaignId = signupSFObjectId,
            )
            sbc.create(junction_obj)
        
        plone_utils = getToolByName(self.context, 'plone_utils')
        plone_utils.addPortalMessage(_(u"We've received your registration."))
        
        # redirect and setup a flag for the registration viewlet to inspect
        if hasattr(self.request, 'response'):
            self.request.response.redirect(self.context.absolute_url() + "?rsvp-complete=1")
    
    def render(self):
        self.setUpWidgets(ignore_request=False)
        self.form_result = self.template()
        return self.form_result
    
    def handle_register_action_failure(self, action, data, errors):
        # set the status
        self.status = _('There were errors')
        
        # determine whether the over capacity flag exists as set within is_still_rsvpable
        if data.has_key('over-capacity-failure') and data['over-capacity-failure']:
            self.status = _("""Sorry, but your registration failed. There's no longer any space to attend.""")
        else:
            plone_utils = getToolByName(self.context, 'plone_utils')
            plone_utils.addPortalMessage(self.status)
            self.request.response.redirect(self.context.absolute_url() + "?" + "&".join(["form.%s=%s" % (k, v) for k, v in data.items() if v]))
        
    


