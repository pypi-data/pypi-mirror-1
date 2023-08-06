import unittest

from DateTime import DateTime

from zope.interface import alsoProvides
from zope.publisher.browser import TestRequest
from zope.component import getMultiAdapter

from Products.CMFCore.utils import getToolByName

from collective.salesforce.rsvp.tests.base import SFRSVPTestCase
from collective.salesforce.rsvp.browser import registration
from collective.salesforce.rsvp import interfaces
from collective.salesforce.rsvp.config import MAX_CAPACITY_FIELD, \
    IS_WAITLISTABLE_FIELD, ATTENDEE_CNT_FIELD

class TestRegistrationViewlet(SFRSVPTestCase):
    """Our registration viewlet is responsible for presenting a variety of
       context specific messages to the potential registrant (i.e. signup here,
       registration full, registration full, but get on the wait list).  Here
       we test the various scenarios.
    """
    def afterSetUp(self):
        SFRSVPTestCase.afterSetUp(self)
        
        # get tools
        self.sbc = getToolByName(self.portal, 'portal_salesforcebaseconnector')
        self.utils = getToolByName(self.portal, 'plone_utils')
        
        # add an event for use
        self.folder.invokeFactory("Event", 'rsvpable')
        self.rsvpable = self.folder.rsvpable
        
        # apply the marker interface to our event object
        alsoProvides(self.rsvpable, interfaces.ISalesforceRSVPable)
        
        # get our viewlet
        request = self.app.REQUEST
        context = self.rsvpable
        self.rsvp_viewlet = registration.RegistrationViewlet(context, request, None, None)
    
    def test_is_waitlistable(self):
        # by default, a rsvpable object shouldn't be waitlistable
        self.failIf(self.rsvp_viewlet.isWaitlistable())
        
        # let's configure our rsvpable object to accept waitlist attendees
        # and ensure that our viewlet can accurately present this reality
        self.rsvpable.getField('acceptWaitlistRegistrantsField').set(self.rsvpable, IS_WAITLISTABLE_FIELD)
        sfCampaignId = self._configureRSVPableObject(self.rsvpable)
        self._setWaitlistableStatus(sfCampaignId, IS_WAITLISTABLE_FIELD, True)
        
        self.failUnless(self.rsvp_viewlet.isWaitlistable())
    
    def test_can_outsource_registration(self):
        # by default, a rsvpable object will be configured to use the 
        # default registration form and therefore will fail
        # a test of canOutsourceRegistration
        self.failIf(self.rsvp_viewlet.canOutsourceRegistration())
        
        # let's configure our rsvpable object to provide a custom reg form
        # and ensure that our viewlet can accurately present this reality
        # we'll just use our own UID for the moment.
        self.rsvpable.getField('customRegistration').set(self.rsvpable, self.rsvpable.UID())
        self.failUnless(self.rsvp_viewlet.canOutsourceRegistration())
        
    def test_viewlet_provides_proper_outsourced_registration_url(self):
        # we start out with nothing
        self.failIf(self.rsvp_viewlet.outsourcedRegistrationURL())
        
        # assuming a custom registration has been set ...
        self.rsvpable.getField('customRegistration').set(self.rsvpable, self.rsvpable.UID())
        
        # ... and the unique id of a Salesforce.com object
        # serves as the RSVPable object...
        self.rsvpable.getField('sfObjectId').set(self.rsvpable, '0089HG_BOGUS_PLONE_TEST_CASE')
        
        # our outsourcedUrl should have...
        outsourcedUrl = self.rsvp_viewlet.outsourcedRegistrationURL()
        
        # the custom registration url
        self.failUnless(self.rsvpable.absolute_url() in outsourcedUrl)
        
        # the documented query string value
        self.failUnless('signup-object-id' in outsourcedUrl)
        
        # the actual value of the associated RSVPable SF object
        self.failUnless('0089HG_BOGUS_PLONE_TEST_CASE' in outsourcedUrl)
    
    def test_viewlet_is_under_capacity(self):
        # we should always start out under capacity
        self.failUnless(self.rsvp_viewlet.isUnderCapacity())
        
        sfCampaignId = self._configureRSVPableObject(self.rsvpable)
        
        # configure our rsvpable event to enforce capacity
        # we start out with a very low threshold of zero
        self.rsvpable.getField('maxCapacityField').set(self.rsvpable, MAX_CAPACITY_FIELD)
        self.rsvpable.getField('attendeeCountField').set(self.rsvpable, ATTENDEE_CNT_FIELD)
        
        # prior to setting the actual max capacity number w/in Salesforce we'll have a 
        # value that we can't cast to an integer and therefore there is no real max 
        # capacity, we ensure that our code doesn't crumple under this scenario
        self.failUnless(self.rsvp_viewlet.isUnderCapacity())
        
        # now we'll actuall set something that can be cast to an int
        self._setMaxCapacityValue(sfCampaignId, MAX_CAPACITY_FIELD, 0)
        
        # with a capacity of zero, we should definitely be
        # at capacity from the get go
        self.failIf(self.rsvp_viewlet.isUnderCapacity())
        
        # now we try something a bit more ambitious, we require a registration
        self._setMaxCapacityValue(sfCampaignId, MAX_CAPACITY_FIELD, 1)
        
        # signups are on...
        self.failUnless(self.rsvp_viewlet.isUnderCapacity())
        
        # add an attendee the old fashioned way
        lead_obj = dict(type='Lead',
            FirstName = 'Ploney',
            LastName = 'McPlonesontestcase',
            Email = 'plone@mcplonesontestcase.name',
            Phone = '(555) 555-1234',
            Company = "[not provided]",  # and some required fields
            LeadSource = "Event Signup", # for the lead object
        )
        
        # make sure we're not going to get lead collisions later on
        assert 0 == self.sbc.query(['Id',],'Lead',"FirstName = '%s' AND LastName = '%s' AND Email = '%s' AND Phone = '%s'" % (
            lead_obj['FirstName'],
            lead_obj['LastName'],
            lead_obj['Email'],
            lead_obj['Phone'],))['size']
        
        # setup our lead for cleanup
        lead_res = self.sbc.create(lead_obj)
        lead_id = lead_res[0]['id']
        self._toCleanUp.append(lead_id)
        
        # create a CampaignMember junction object the old fashioned way
        cm_obj = dict(type='CampaignMember',
            LeadId = lead_id,
            CampaignId = sfCampaignId,
            Status = 'Responded',            
        )
        
        cm_res = self.sbc.create(cm_obj)
        self._toCleanUp.append(cm_res[0]['id'])
        
        # with a capacity of zero, we should definitely be
        # at capacity from the get go
        self.failIf(self.rsvp_viewlet.isUnderCapacity())
    
    def test_viewlet_rendering(self):
        # setup a resonable time for RSVPable object
        now = DateTime()
        self.rsvpable.setExpirationDate(now + 1)
        
        # since we're not yet tied to a Salesforce object
        # the user shouldn't see any registration capabilities
        # within our viewlet
        self.failIf(self.rsvp_viewlet.render())
        
        # once the rsvpable object is configured
        # default scenario would be to present the form, 
        # since there's unlimited capacity to start
        sfCampaignId = self._configureRSVPableObject(self.rsvpable)
        self.failUnless('name="form.first_name"' in self.rsvp_viewlet.render())
        self.failUnless('name="form.last_name"' in self.rsvp_viewlet.render())
        
        # setup an associated campaign and set the capacity to zero, set count field
        self.rsvpable.getField('maxCapacityField').set(self.rsvpable, MAX_CAPACITY_FIELD)
        self.rsvpable.getField('attendeeCountField').set(self.rsvpable, ATTENDEE_CNT_FIELD)
        self._setMaxCapacityValue(sfCampaignId, MAX_CAPACITY_FIELD, 0)
        
        # with waitlisting defaulting to off, we should see...
        self.failUnless("registration is full" in self.rsvp_viewlet.render())
        
        # with a capacity of zero, but waitlists accepted, we see the form...
        self.rsvpable.getField('acceptWaitlistRegistrantsField').set(self.rsvpable, IS_WAITLISTABLE_FIELD)
        self._setWaitlistableStatus(sfCampaignId, IS_WAITLISTABLE_FIELD, True)
        self.failUnless("added to the waitlist" in self.rsvp_viewlet.render())
        self.failUnless('name="form.first_name"' in self.rsvp_viewlet.render())
        
        # next we configure our own custom form...
        self.rsvpable.getField('customRegistration').set(self.rsvpable, self.rsvpable.UID())
        
        # we're full, but accepting waitlist rsvps
        # the custom registration url should be presented to the user
        self.failUnless("added to the waitlist" in self.rsvp_viewlet.render())
        self.failUnless(self.rsvpable.absolute_url() in self.rsvp_viewlet.render())
        self.failUnless('signup-object-id' in self.rsvp_viewlet.render())
        
        # boost the capacity to > current number of signups
        self._setMaxCapacityValue(sfCampaignId, MAX_CAPACITY_FIELD, 1)
        
        # we're full, but accepting waitlist rsvps
        # the custom registration url should be presented to the user
        self.failUnless(self.rsvpable.absolute_url() in self.rsvp_viewlet.render())
        self.failUnless('signup-object-id' in self.rsvp_viewlet.render())
        
        # next we reconfigure to use default form
        self.rsvpable.getField('customRegistration').set(self.rsvpable, None)
        
        # setting our event start/end dates to the past -- 
        # make sure we see no registration form
        self.rsvpable.setExpirationDate(now - 1.5)
        self.failIf('name="form.first_name"' in self.rsvp_viewlet.render())
        self.failIf('name="form.last_name"' in self.rsvp_viewlet.render())
    
    def test_viewlet_handles_nonexistant_sfobject(self):
        # a possible scenario is that a user sets up an event
        # for rsvps and long after the event forgets about the lingering
        # relationship between campaign and salesforce.com object and
        # subsequently deletes the campaign from salesforce.com
        # does the registration viewlet handle this scenario gracefully
        # unlikely though it may be...
        
        # some reasonable configuration to the plone content object
        sfCampaignId = self._configureRSVPableObject(self.rsvpable)
        self.rsvpable.getField('maxCapacityField').set(self.rsvpable, MAX_CAPACITY_FIELD)
        self.rsvpable.getField('attendeeCountField').set(self.rsvpable, ATTENDEE_CNT_FIELD)
        
        # ... after sometime, we directly delete the associated campaign from Salesforce.com
        # and remove it from the to be deleted list upon test case cleanup
        self.sbc.delete([sfCampaignId,])
        self._toCleanUp.remove(sfCampaignId)
        
        # we shouldn't have any capacity
        self.assertEqual(None, self.rsvp_viewlet.isUnderCapacity())
        
        # ... and we shouldn't be getting anything
        # back from our viewlet's rendering ...
        self.failIf(self.rsvp_viewlet.render())
    
    def test_viewlet_handles_misconfiguration_of_capacity_fields(self):
        # a user could choose a field that represents the attendeeCountField
        # or the maxCapacityField, but not both together.  Since these are
        # used to suggest current event capacities in conjunction, even
        # though the user should see validation, we want to make sure
        # we're covered for this situation.
        # some reasonable configuration to the plone content object
        sfCampaignId = self._configureRSVPableObject(self.rsvpable)
        self.rsvpable.getField('maxCapacityField').set(self.rsvpable, MAX_CAPACITY_FIELD)
        # ^^^ notice the lack of attendeeCountField...
        
        # in this scenario, we can't develop an opinion about capacity
        # so we we'll let in registrants in
        self.failUnless(self.rsvp_viewlet.isUnderCapacity())
        
        # and the converse ...
        self.rsvpable.getField('attendeeCountField').set(self.rsvpable, ATTENDEE_CNT_FIELD)
        self.rsvpable.getField('maxCapacityField').set(self.rsvpable, '')
        # ^^^ notice the unsetting of maxCapacityField
        
        # we should still let registrants in
        self.failUnless(self.rsvp_viewlet.isUnderCapacity())
        
        # finally, what about a bogus field or one that was configured and then deleted
        self.rsvpable.getField('attendeeCountField').set(self.rsvpable, 'MyBogusAttendeeCountFieldThatWasDeleted__c')
        self.rsvpable.getField('maxCapacityField').set(self.rsvpable, MAX_CAPACITY_FIELD)
        
        # and we still yet let registrants in
        self.failUnless(self.rsvp_viewlet.isUnderCapacity())
    
    def test_registration_viewlet_post_registration(self):
        # here we simulate the request after the registration
        # has been completed to ensure that the user isn't
        # presented with any registration options after completing 
        # the form.  it's fine if the page is reloaded, we just
        # want all signs to suggest success when relevant
        
        # get our viewlet in a registration completed way
        request = self.app.REQUEST
        request.set('rsvp-complete', 1)
        context = self.rsvpable
        completed_viewlet = registration.RegistrationViewlet(context, request, None, None)
        
        self.failIf(self.rsvp_viewlet.render())
    


class TestDefaultRegistrationForm(SFRSVPTestCase):
    """Our product provides a default registration form implementing the
       obvious scenario of creating a brand new lead object and the lead/campaign
       junction object with the appropriate unique id of the created lead and
       the chosen unique id provided by the contextual rsvpable object.  In most
       cases, folks will be using PloneFormGen with the Salesforce PFG Adapter which
       gives pretty complete control over the entire registration process and it's 
       communication with Salesforce.com.  Salesforce PFG Adapter and its ilk 
       aren't explicit dependencies though.
    """
    def afterSetUp(self):
        SFRSVPTestCase.afterSetUp(self)
        
        # add an event for use
        self.folder.invokeFactory("Event", 'rsvpable')
        self.rsvpable = self.folder.rsvpable
        
        # apply the marker interface to our event object
        alsoProvides(self.rsvpable, interfaces.ISalesforceRSVPable)
        
        # get base connector for use
        self.sbc = getToolByName(self.portal, 'portal_salesforcebaseconnector')
        
        # get our viewlet
        request = self.app.REQUEST
        context = self.rsvpable
        self.rsvp_viewlet = registration.RegistrationViewlet(context, request, None, None)
        
    
    def test_registration_incomplete_data(self):
        # setup an incomplete request that will fail validation
        incomplete_request = TestRequest(form={'form.first_name':u'John',
                                               'form.last_name':u'',
                                               'form.actions.register':'register'})
        incomplete_request.RESPONSE = incomplete_request.response
        
        # get the form object
        registration_form = getMultiAdapter((self.rsvpable, incomplete_request), name='registration-form')
        
        # call update (aka submit) on the form, see TestRequest above
        registration_form.update()
        self.failUnless(u'There were errors' in registration_form.status)
    
    def test_registration_email_invariant(self):
        # setup an incomplete request that will fail validation
        invalid_email_request = TestRequest(form={'form.first_name':'Ploney',
                                    'form.last_name':'McPlonesontestcase',
                                    'form.email':'this is not a valid email address',
                                    'form.company':'Plone RSVP Test Case Organization',
                                    'form.phone':'(555) 555-1234',
                                    'form.actions.register':'register'})
        invalid_email_request.RESPONSE = invalid_email_request.response
        
        # get the form object
        registration_form = getMultiAdapter((self.rsvpable, invalid_email_request), name='registration-form')
        
        # call update (aka submit) on the form, see TestRequest above
        registration_form.update()
        self.failUnless(u'There were errors' in registration_form.status)
    
    def test_bait_n_switch_signup_form_after_registration_overage(self):
        # bait 'n switch is not really the appropriate term, however
        # we have a problem whereby the registration status is checked
        # on page load (i.e. should we be saying this activity is overbooked)
        # despite the fact that many could load the form similtaneously and
        # take varying lengths of time to secure their position in line
        # this confirms that we check capacity and waitlist status an
        # additional time after completion of the form and paves the way for 
        # demonstration code that may do the same in a custom PFG form
        
        # configure our object and tie it to a campaign for rsvps
        sfCampaignId = self._configureRSVPableObject(self.rsvpable)
        
        # we setup a capacity of 1 and take the default of no waitlisting
        self.rsvpable.getField('maxCapacityField').set(self.rsvpable, MAX_CAPACITY_FIELD)
        self.rsvpable.getField('attendeeCountField').set(self.rsvpable, ATTENDEE_CNT_FIELD)
        self._setMaxCapacityValue(sfCampaignId, MAX_CAPACITY_FIELD, 1)
        
        # the user "checks" whether they can still register on page load
        self.failUnless(self.rsvp_viewlet.isUnderCapacity())
        
        # but at the same time another user registers. we don't 
        # care how, so we add an attendee the old fashioned way
        lead_obj = dict(type='Lead',
            FirstName = 'Ploney',
            LastName = 'McPlonesontestcase',
            Email = 'plone@mcplonesontestcase.name',
            Phone = '(555) 555-1234',
            Company = "[not provided]",  # and some required fields
            LeadSource = "Event Signup", # for the lead object
        )
        
        # make sure we're not going to get lead collisions later on
        assert 0 == self.sbc.query(['Id',],'Lead',"FirstName = '%s' AND LastName = '%s' AND Email = '%s' AND Phone = '%s'" % (
            lead_obj['FirstName'],
            lead_obj['LastName'],
            lead_obj['Email'],
            lead_obj['Phone'],))['size']
        
        # setup our lead for cleanup
        lead_res = self.sbc.create(lead_obj)
        lead_id = lead_res[0]['id']
        self._toCleanUp.append(lead_id)
        
        # create a CampaignMember junction object the old fashioned way
        cm_obj = dict(type='CampaignMember',
            LeadId = lead_id,
            CampaignId = sfCampaignId,
            Status = 'Responded',            
        )
        
        cm_res = self.sbc.create(cm_obj)
        self._toCleanUp.append(cm_res[0]['id'])
        
        # now if we were to talk to the viewlet again, 
        # we we wouldn't be encouraged to register ...
        self.failIf(self.rsvp_viewlet.isUnderCapacity())
        # ... but of course we can still fill out the already loaded form and we do
        too_late_request = TestRequest(form={'form.first_name':'TestCaseTooLate',
                                    'form.last_name':'RSVP-Registrant',
                                    'form.email':'plone@testcasetoolateregistrant.name',
                                    'form.actions.register':'register'})
        too_late_request.RESPONSE = too_late_request.response
        registration_form = getMultiAdapter((self.rsvpable, too_late_request), 
                                            name='registration-form')
        
        # call update (aka submit) on the form, see TestRequest above
        registration_form.update()
        
        too_late_query = self.sbc.query(['Id',],'Lead',"FirstName = '%s' AND LastName = '%s' AND Email = '%s'" % (
            too_late_request.form['form.first_name'],
            too_late_request.form['form.last_name'],
            too_late_request.form['form.email'],))
        
        # just in case we're destined for failure, we get ready to cleanup
        if len(too_late_query['records']):
            self._toCleanUp.append(too_late_query['records'][0]['Id'])
        
        # but fortunately our action validation saves the day and doesn't
        # allow the registration to go through...
        self.failUnless(u'Sorry, but your registration failed' in registration_form.status)
        self.assertEqual(0, too_late_query['size'])
        
    
    def test_successful_registration_interaction_with_salesforce(self):
        # setup a reasonable request
        request = TestRequest(form={'form.first_name':'Ploney',
                                    'form.last_name':'McPlonesontestcase',
                                    'form.email':'plone@mcplonesontestcase.name',
                                    'form.company':'Plone RSVP Test Case Organization',
                                    'form.phone':'(555) 555-1234',
                                    'form.actions.register':'register'})
        request.RESPONSE = request.response
        
        # make sure we're not going to get lead collisions later on
        assert 0 == self.sbc.query(['Id',],'Lead',"FirstName = '%s' AND LastName = '%s' AND Email = '%s' AND Company = '%s' AND Phone = '%s'" % (
            request.form['form.first_name'],
            request.form['form.last_name'],
            request.form['form.email'],
            request.form['form.company'],
            request.form['form.phone'],))['size']
        
        # configure our object and tie it to a campaign for rsvps
        sfCampaignId = self._configureRSVPableObject(self.rsvpable)
        
        # get the form object
        registration_form = getMultiAdapter((self.rsvpable, request), name='registration-form')
        
        # call update (aka submit) on the form, see TestRequest above
        registration_form.update()
        
        # get ready to cleanup after ourselves
        lead_res = self.sbc.query(['Id','FirstName','LastName','Email','Company','Phone',],
            'Lead',"FirstName = '%s' AND LastName = '%s' AND Email = '%s' AND Company = '%s' AND Phone = '%s'" % (
            request.form['form.first_name'],
            request.form['form.last_name'],
            request.form['form.email'],
            request.form['form.company'],
            request.form['form.phone'],))
        
        lead_id = lead_res['records'][0]['Id']
        self._toCleanUp.append(lead_id)
        
        # get the junction object
        junc_res = self.sbc.query(['LeadId','CampaignId','Id',],
                                   'CampaignMember',"CampaignId = '%s' AND LeadId = '%s'" % (sfCampaignId, lead_id))
        self._toCleanUp.append(junc_res['records'][0]['Id'])
        
        # with that simple form completion, we want to see ...
        ## one newly created lead object
        self.assertEqual(1, lead_res['size'])
        self.assertEqual(request.form['form.first_name'], lead_res['records'][0]['FirstName'])
        self.assertEqual(request.form['form.last_name'], lead_res['records'][0]['LastName'])
        self.assertEqual(request.form['form.email'], lead_res['records'][0]['Email'])
        self.assertEqual(request.form['form.company'], lead_res['records'][0]['Company'])
        self.assertEqual(request.form['form.phone'], lead_res['records'][0]['Phone'])
        
        # one CampaignMember junction object, w/ appropriate LeadId and 
        self.assertEqual(1, junc_res['size'])
        self.assertEqual(sfCampaignId, junc_res['records'][0]['CampaignId'])
        self.assertEqual(lead_id, junc_res['records'][0]['LeadId'])
        
        # and with that, a lead associated with our campaign
        # we look at NumberOfLeads, rather than NumberOfResponses b/c
        # the default CampaignMemberStatus for a Campaign is sent
        campaign_res = self.sbc.retrieve(['NumberOfLeads',],'Campaign',[sfCampaignId,])
        self.assertEqual(1, campaign_res[0]['NumberOfLeads'])
    
    def test_registration_without_optional_fields(self):
        """Confirms optional fields are actually optional"""
        # setup a reasonable request w/out optional fields included
        request = TestRequest(form={'form.first_name':'Ploney',
                                    'form.last_name':'McPlonesontestcase',
                                    'form.email':'plone@mcplonesontestcase.name',
                                    'form.actions.register':'register'})
        request.RESPONSE = request.response
        
        # make sure we're not going to get lead collisions later on
        assert 0 == self.sbc.query(['Id',],'Lead',"FirstName = '%s' AND LastName = '%s' AND Email = '%s'" % (
            request.form['form.first_name'],
            request.form['form.last_name'],
            request.form['form.email'],))['size']
        
        # configure our object and tie it to a campaign for rsvps
        sfCampaignId = self._configureRSVPableObject(self.rsvpable)
        
        # get the form object
        registration_form = getMultiAdapter((self.rsvpable, request), name='registration-form')
        
        # call update (aka submit) on the form, see TestRequest above
        registration_form.update()
        
        # get ready to cleanup after ourselves
        lead_res = self.sbc.query(['Id','FirstName','LastName','Email','Company','Phone',],
            'Lead',"FirstName = '%s' AND LastName = '%s' AND Email = '%s' AND Company = '[not provided]' AND Phone = ''" % (
            request.form['form.first_name'],
            request.form['form.last_name'],
            request.form['form.email'],))
        
        lead_id = lead_res['records'][0]['Id']
        self._toCleanUp.append(lead_id)
        
        # get the junction object
        junc_res = self.sbc.query(['LeadId','CampaignId','Id',],
                                   'CampaignMember',"CampaignId = '%s' AND LeadId = '%s'" % (sfCampaignId, lead_id))
        self._toCleanUp.append(junc_res['records'][0]['Id'])
        
        # with that simple form completion, we want to see ...
        ## one newly created lead object
        self.assertEqual(1, lead_res['size'])
        self.assertEqual(request.form['form.first_name'], lead_res['records'][0]['FirstName'])
        self.assertEqual(request.form['form.last_name'], lead_res['records'][0]['LastName'])
        self.assertEqual(request.form['form.email'], lead_res['records'][0]['Email'])
        self.assertEqual("[not provided]", lead_res['records'][0]['Company'])
        
        # one CampaignMember junction object, w/ appropriate LeadId and 
        self.assertEqual(1, junc_res['size'])
        self.assertEqual(sfCampaignId, junc_res['records'][0]['CampaignId'])
        self.assertEqual(lead_id, junc_res['records'][0]['LeadId'])
        
        # and with that, a lead associated with our campaign
        # we look at NumberOfLeads, rather than NumberOfResponses b/c
        # the default CampaignMemberStatus for a Campaign is sent
        campaign_res = self.sbc.retrieve(['NumberOfLeads',],'Campaign',[sfCampaignId,])
        self.assertEqual(1, campaign_res[0]['NumberOfLeads'])
    


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestRegistrationViewlet))
    suite.addTest(unittest.makeSuite(TestDefaultRegistrationForm))
    return suite
