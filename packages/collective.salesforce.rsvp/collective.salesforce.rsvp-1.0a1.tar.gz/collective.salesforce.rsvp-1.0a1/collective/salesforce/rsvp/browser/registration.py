from zope.interface import implements
from zope.component import getMultiAdapter

from beatbox import SoapFaultError

from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from collective.salesforce.rsvp.interfaces import IRegistrationViewlet
from collective.salesforce.rsvp.browser.forms import IRegistrationForm
from collective.salesforce.rsvp import RSVPMessageFactory as _

class RegistrationViewlet(ViewletBase):
    """See ..interfaces/IRegistrationViewlet
    """
    implements(IRegistrationViewlet)
    
    def __init__(self, context, request, view, manager):
        super(RegistrationViewlet, self).__init__(context, request, view, manager)
        self.sbc = getToolByName(self.context, 'portal_salesforcebaseconnector')
        self.utils = getToolByName(self.context, 'plone_utils')
    
    @property
    def associated_sfobject_id(self):
        return self.context.getField('sfObjectId').get(self.context)
    
    @property
    def sfobject_signup_type(self):
        return self.context.getField('sfObjectSignupType').get(self.context)
    
    _render = ViewPageTemplateFile('templates/registration-full.pt')
    
    def _retrieveRSVPableSettings(self, requested_fields):
        return self.sbc.retrieve(
            requested_fields, 
            self.sfobject_signup_type, 
            [self.associated_sfobject_id,])
    
    def render(self):
        """See ..interfaces/IRegistrationViewlet
        """
        form_tmpl =  """<form action="%s/@@registration-form" method="post" class="edit-form" """
        form_tmpl += """ enctype="multipart/form-data" """
        form_tmpl += """ id="zc.page.browser_form"> """
        
        # figure out what our current capacity status is...
        under_cap_status = self.isUnderCapacity()
        
        # in order to get into our registration related options, the following must be true:
        #  1) an expiration date that's either none or in the future (since we're talking 
        #     AT-objects here and everything using this should have that) 
        #  2) a Salesforce.com object id exists
        #  3) under_cap_status is not None, which would signify that an item has been removed
        #  4) the 'rsvp-complete' flag (setup view the registration form 
        #     must be absent and evaluate to not bool() upon render
        if (self.context.getExpirationDate() is None or self.context.getExpirationDate().isFuture()) and \
           (self.associated_sfobject_id and under_cap_status is not None) and \
           not (self.request.has_key('rsvp-complete') and self.request['rsvp-complete']):
            if under_cap_status:
                if self.canOutsourceRegistration():
                    # our lead in text lies here
                    self._render = ViewPageTemplateFile('templates/registration-link.pt')
                
                    # we prepend that to the link to the registration form
                    return self._render() + self.outsourcedRegistrationURL()
                else:
                    # just return the rendered formlib form
                    reg_form = self.context.restrictedTraverse("@@registration-form")
                    return form_tmpl % self.context.absolute_url() + reg_form.render() + """</form>"""
            else:
                if self.isWaitlistable():
                    if self.canOutsourceRegistration():
                        # our lead in text lies here
                        self._render = ViewPageTemplateFile('templates/warning-registration-link.pt')
                    
                        # we prepend that to the link to the registration form
                        return self._render() + self.outsourcedRegistrationURL()
                    else:
                        # our lead in text lies here
                        self._render = ViewPageTemplateFile('templates/warning-registration-form.pt')
                    
                        # we prepend that to the html that our formlib class renders
                        return self._render() + form_tmpl % self.context.absolute_url() \
                                              + self.context.restrictedTraverse("@@registration-form").render() + """</form>"""
                else:
                    # we'll take the default in this case
                    pass
                
            return self._render()
            
        return u""
    
    def isWaitlistable(self):
        """See ..interfaces/IRegistrationViewlet
        """
        waitlistable_field = self.context.getField('acceptWaitlistRegistrantsField').get(self.context)
        
        # XXX we need to share queries here
        if waitlistable_field:
            # it's worth inspecting salesforce.com to determine waitlistability
            waitlistable_status_res = self._retrieveRSVPableSettings([waitlistable_field,])
            
            # The criteria for accepting waitlist applications are:
            #   1) we have exactly one item from Salesforce.com for the id
            #   2) the resulting item value is of boolean type
            #   3) the resulting item value is actually true
            if len(waitlistable_status_res) == 1 and \
               type(waitlistable_status_res[0][waitlistable_field]) == type(bool()) and \
               waitlistable_status_res[0][waitlistable_field] is True:
                return True
        
        return False
    
    def isUnderCapacity(self):
        """See ..interfaces/IRegistrationViewlet
        """
        def _except_only_if_invalid_field(exc_info):
            # note: this will go away once we handle
            # the myriad of fault codes that Salesforce.com
            # can return and raise more sepecific exceptions
            # we do this now, so that we don't clobber 
            # reasonable exceptions and in the future where
            # we have an invalid field exception, the appropriate
            # test will fail and we can pull out this error handling.
            if exc_info[1].faultCode == 'INVALID_FIELD':
                return
            else:
                raise exc_info[0], exc_info[1], exc_info[2]
        
        maxCapacityField = self.context.getField('maxCapacityField').get(self.context)
        attendeeCountField = self.context.getField('attendeeCountField').get(self.context)
        
        # if we don't have this stuff, don't even bother trying to figure it out
        if maxCapacityField and attendeeCountField:
            # we need to get the max capacity value, we'll also 
            # get the attendee count value while we're at it
            try:
                rsvp_status_res = self.sbc.retrieve(
                    [attendeeCountField, maxCapacityField], 
                    self.sfobject_signup_type, 
                    [self.associated_sfobject_id,])
            except:
                # something is amiss with our query
                import sys
                
                # let's determine if we should raise an exceptions
                _except_only_if_invalid_field(sys.exc_info())
                
                # we hold no opinion about rsvp capacity
                return True
            
            # the object may no longer exist
            if len(rsvp_status_res) == 1:
                # we have an item, so we can move along
                pass
            else:
                # the salesforce object no longer exists
                # so there's no concept of capacity
                # we return and test for none in this scenario
                return None
            
            try:
                if int(rsvp_status_res[0][maxCapacityField]) == 0:
                    # never was any capacity
                    return False
            except TypeError:
                # can't convert max value to int for comparison
                # must still have room for rsvps
                return True
            
            # we've delayed long enough, get into the rigors of checking capacity
            currAttendeeNum = rsvp_status_res[0][attendeeCountField]
            
            if int(currAttendeeNum) >= int(rsvp_status_res[0][maxCapacityField]):
                return False
                
        return True
    
    def canOutsourceRegistration(self):
        """See ..interfaces/IRegistrationViewlet
        """
        if self.context.getField('customRegistration').getRaw(self.context):
            return True
        
        return False
    
    def outsourcedRegistrationURL(self):
        """See ..interfaces/IRegistrationViewlet
        """
        if self.canOutsourceRegistration():
            # we first assume a UID
            uid_cat = getToolByName(self.context, 'uid_catalog')
            results = uid_cat.searchResults(
                UID = self.context.getField('customRegistration').getRaw(self.context),
            )
            
            if len(results):
                return _(u"""<a href="%s?signup-object-id=%s">Register</a>""" % (results[0].getObject().absolute_url(), 
                                                   self.associated_sfobject_id))
        
        return
    

