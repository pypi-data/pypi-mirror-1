from zope.interface import implements
from zope.component import adapts
from archetypes.schemaextender.interfaces import ISchemaExtender

from Products.Archetypes import atapi
from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget

from collective.salesforce.rsvp.config import RSVP_SCHEMATA
from collective.salesforce.rsvp.interfaces import ISalesforceRSVPable
from collective.salesforce.rsvp import fields
from collective.salesforce.rsvp import RSVPMessageFactory as _

class RSVPExtender(object):
    """See ISchemaExtender
    """
    implements(ISchemaExtender)
    adapts(ISalesforceRSVPable)
    
    _fields = [
            fields.RSVPStringField('enableCustomRegistration',
                required=False,
                searchable=False,
                default='default',
                enforceVocabulary=True,
                schemata=RSVP_SCHEMATA,
                widget=atapi.SelectionWidget(
                    label=_(u"Do you want to use the default or a custom registration form?"),
                    description = _(u"Please note: this is intended to simplify the editing process \
                                      and doesn't have an actual barring upon whether the default \
                                      registration or custom alternative is used.  That's determined by \
                                      the value within the 'Custom Registration Form' field."),
                ),
                vocabulary=atapi.DisplayList((
                    ('default',_(u"""I want to use the default registration form to create 'Leads' \
                                     associated with my 'Campaign'""")),
                    ('custom',_(u"""I created (or will create) a custom registration form with fields of my choosing \
                                    that map to Salesforce objects of my choosing.""")),)),
            ),
            fields.RSVPReferenceField('customRegistration',
                required=False,
                searchable=False,
                relationship = 'isCustomRegistration',
                multiValued = False,
                isMetadata = True,
                languageIndependent = False,
                schemata=RSVP_SCHEMATA,
                widget=ReferenceBrowserWidget(
                    allow_search = True,
                    allow_browse = True,
                    show_indexes = False,
                    force_close_on_insert = True,
                    label = _(u"Custom Registration Form"),
                    description = _(u"""If you require more flexibility (in terms of the registration fields \
                                        presented to a potential attendee and/or the types of records created upon \
                                        successful registration in Salesforce.com), you can select your own custom \
                                        registration form. This should map the form fields to the intended \
                                        Salesforce object(s) that represent your 'Attendee' and the 'Attendance' \
                                        junction. The Salesforce 'Id' representing the object to which your \
                                        'Attendees' are related will be passed to your custom registration form under \
                                        the name 'signup-object-id', so take note to account for this appropriately."""),
                    visible = {'edit' : 'visible', 'view' : 'invisible' },
                ),
            ),
            fields.RSVPObjTypeField('sfObjectSignupType',
                required=False,
                searchable=False,
                default='Campaign',
                enforceVocabulary=True,
                schemata=RSVP_SCHEMATA,
                widget=atapi.SelectionWidget(
                    label=_(u"Associated Salesforce Object Type"),
                    description = _(u"""Choose the Salesforce object that you want to associate your attendees with. \
                                        The default is Campaign."""),
                ),
            ),
            fields.RSVPStringField('sfObjectId',
                required=True,
                searchable=False,
                schemata=RSVP_SCHEMATA,
                widget=atapi.StringWidget(
                    label=_(u"The 'Id' of the associated Salesforce Object"),
                    description=_(u"Provide the Salesforce auto-generated unique id that you want to associate your \
                                    attendees with."),
                ),
            ),
            fields.RSVPStringField('limitRegistrationCapacity',
                required=False,
                searchable=False,
                default='no',
                enforceVocabulary=True,
                schemata=RSVP_SCHEMATA,
                widget=atapi.SelectionWidget(
                    label=_(u"Would you like to limit registrations at a particular amount?"),
                    description = _(u"Please note: this is intended to simplify the editing process \
                                      and doesn't have an actual barring upon the limiting of actual \
                                      registrations for this item. That's determined with the correct \
                                      configuration of the 'Maximum Capacity Field' and 'Attendee Count \
                                      Field'."),
                ),
                vocabulary=atapi.DisplayList((
                    ('no',_(u"""I don't need to limit registrations (useful if you have plenty of capacity for \
                                expected attendance levels or you plan to do some additional screening of 
                                potential registrants say via a offline application or upon receiving some payment)""")),
                    ('yes',_(u"""I need to limit the registrations for this item due to capacity constraints (if so, \
                                 you'll need to correctly configure several related fields below.)""")),)),
            ),
            fields.RSVPSelectionField('maxCapacityField',
                required=False,
                searchable=False,
                schemata=RSVP_SCHEMATA,
                widget=atapi.SelectionWidget(
                    label = _(u'Maximum Capacity Field'),
                    description = _(u"""Select the field for the chosen 'Associated Salesforce Object Type' that \
                                        represents the maximum capacity for attendees for the given activity. Providing \
                                        no 'Maximum Capacity Field' or failing to pick an Salesforce field of type \
                                        Integer signifies unlimited capacity. In conjunction with the 'Waitlist \
                                        Registrants Allowed?' field, this value will be used to determine whether a \
                                        potential attendee can still signup to be placed on the waitlist."""),
                    visible = {'edit' : 'visible', 'view' : 'invisible' },
                ),
            ),
            fields.RSVPSelectionField('attendeeCountField',
                required=False,
                searchable=False,
                schemata=RSVP_SCHEMATA,
                widget=atapi.SelectionWidget(
                    label = _(u'Attendee Count Field'),
                    description = _(u"""Select the field on the chosen 'Associated Salesforce Object Type' which \
                                        represents the current number of confirmed attendees. This should be an \
                                        auto-incrementing field that always represents the exact number of attendees \
                                        that have successfully registered for the given event. If you are using \
                                        Campaigns, the 'NumberOfResponses' field is a reasonable default and an example \
                                        of an auto-incrementing field."""),
                    visible = {'edit' : 'visible', 'view' : 'invisible' },
                ),
            ),
            fields.RSVPSelectionField('acceptWaitlistRegistrantsField',
                required=False,
                searchable=False,
                schemata=RSVP_SCHEMATA,
                widget=atapi.SelectionWidget(
                    label=_(u"Accepting Waitlist Registrants Field"),
                    description=_(u"""The field on the chosen 'Associated Salesforce Object Type' which \
                                    represents whether or not you accept waitlisted registrations for the \
                                    Salesforce.com item for which you're accepting RSVPs. This must be a \
                                    'Checkbox' field, which returns a true or false value. In the case of a \
                                    misconfiguration, waitlist registrations will not be allowed. In the case \
                                    where waitlisted registrations are allowed, the form will continue to \
                                    accept registrations with an appropriate warning. It's recommended that \
                                    waitlisted registrants be reminded via any confirmation e-mails of their waitlist \
                                    status."""),
                ),
            ),
    ]
    
    def __init__(self, context):
        self.context = context
    
    def getFields(self):
        return self._fields
