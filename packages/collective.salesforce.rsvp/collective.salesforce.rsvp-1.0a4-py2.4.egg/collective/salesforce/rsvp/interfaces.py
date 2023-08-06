from zope.interface import Interface, Attribute
from zope.viewlet.interfaces import IViewlet

class ISalesforceRSVPable(Interface):
    """Marker interface for content objects that are to 
       become Salesforce RSVPable meaning that individuals
       visiting the site can signup for attendance.
    """

class IRSVPConfigurationView(Interface):
    """Provides view methods in regards to the additional RSVP capabilities"""
    def isRSVPEnabled():
        """Returns true if we're implementing the ISalesforceRSVPable interface"""
    
    def enableRSVPs():
        """Accept RSVPs for a given object."""
    
    def disableRSVPs():
        """Disable RSVPs for a given object."""
    

class IDynamicSFObjectFields(Interface):
    """When the content editor clicks to assign or reassign the chosen Salesforce object
       type, update the eligible field options for the complimentary RSVP fields
    """
    def hide_custom_form_selector_if_inactive():
        """Hide the form widget for selecting a custom RSVP form when the configuration 
           page loads unless the IRSVPable context has been configured to use a custom
           RSVP form.  After page load, the visability of this widget is controlled
           by client-side KSS.
        """
    
    def hide_capacity_selectors_if_inactive():
        """kssaction which disables all those fields contained
           within the config controlled list of LIMIT_CAPACITY_HIDABLE
           fields whenever an rsvpable schema is loaded and the 
           current setting is that limits to capacity are not necessary.
           Does so by adding the hiddenStructure class on the relevant ids.
        """
    
    def toggle_capacity_fields_visibility(formvar):
        """kssaction which toggles on/off all those fields contained
           within the config controlled list of LIMIT_CAPACITY_HIDABLE
           fields whenever the user clicks to disable/enable the need to limit
           an item's registration capacity. Does so by adding the hiddenStructure 
           class on the relevant ids.
        """
    
    def toggle_available_field_options(sfobject):
        """Swap out the current list of options for availble fields on the 
           chosen SFObjectType with a whole new set of options.
        """
    

class IRegistrationViewlet(IViewlet):
    """Browser view which accounts for the settings on a ISalesforceRSVPable
       content object and presents various context specific registration options.
    """
    sfobject_signup_type = Attribute(
        """The chosen Salesforce Object type for associating attendance signups.  
           A necessity for the equivalent of:
                `select x, y, z from table_name where id = associated_sfobject_id`
           This is because the Salesforce.com API doesn't support the 
           equivalent of: 
           
                `give me the Salesforce Object of where id = associated_sfobject_id --> now tell my what object type it is`
        """)
    
    associated_sfobject_id = Attribute(
        """The unique id of the chosen Salesforce.com object to be used in association
           with new attendee signups for ISalesforceRSVPable object.""")
    
    def render():
        """Logic determinining which page template is relevant given 
           the context of the RSVPable object.
        """
    
    def isWaitlistable():
        """Return boolean determining whether the associated 
           Salesforce object has been earmarked to accept wait list signups.
        """
    
    def isUnderCapacity():
        """Return boolean determining whether the associated 
           Salesforce object is currently under capacity and
           therefore still accepting signups. If the associated
           Salesforce object no longer exists, we return None,
           which can be tested for in various scenarios where
           we present logical registration options to the user.
        """
    
    def canOutsourceRegistration():
        """Return boolean determining whether the context provides
           a reference to a full signup form or whether the default 
           should be used.
        """
    
    def outsourcedRegistrationURL():
        """If the RSVP enabled content object has a custom registration
           form, returns a url directly to signup form with the unique Id
           of the attendee associated Salesforce.com object.
        """
    

