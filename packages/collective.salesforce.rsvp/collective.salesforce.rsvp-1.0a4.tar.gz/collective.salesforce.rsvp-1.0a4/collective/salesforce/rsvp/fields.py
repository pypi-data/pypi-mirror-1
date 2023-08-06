from Products.CMFCore.utils import getToolByName

from archetypes.schemaextender.field import ExtensionField
from Products.Archetypes import atapi

class RSVPStringField(ExtensionField, atapi.StringField):
    pass

class RSVPSelectionField(ExtensionField, atapi.StringField):
    def Vocabulary(self, content_instance):
        """Populate the vocabulary options with the available
           fields for the configured Salesforce.com object type
           or failing that the default of the 'Campaign' object.
        """
        # get base connector
        sbc = getToolByName(content_instance, 'portal_salesforcebaseconnector')
        curr_sfobject_type = content_instance.getField('sfObjectSignupType').get(content_instance) or 'Campaign'
        obj_schema = sbc.describeSObjects(curr_sfobject_type)[0]
        
        # construct a display list
        fieldDisplay = atapi.DisplayList()
        fieldDisplay.add('', '')
        for k,v in obj_schema.fields.items():
            fieldDisplay.add(k, v.label)
        return fieldDisplay
    

class RSVPReferenceField(ExtensionField, atapi.ReferenceField):
    pass


class RSVPObjTypeField(ExtensionField, atapi.StringField):
    def Vocabulary(self, content_instance):
        """Populate the vocabulary options with the available
           objects for the configured Salesforce.com instance.
        """
        # get base connector
        sbc = getToolByName(content_instance, 'portal_salesforcebaseconnector')
        
        # get the elible types
        types = sbc.describeGlobal()['types']
        
        # construct a display list
        typesDisplay = atapi.DisplayList()
        for t in types:
            typesDisplay.add(t, t)
        return typesDisplay
    


