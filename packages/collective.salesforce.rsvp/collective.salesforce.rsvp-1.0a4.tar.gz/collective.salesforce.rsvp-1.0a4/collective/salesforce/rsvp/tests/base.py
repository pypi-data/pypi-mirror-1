import unittest
import transaction

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite, onsetup
from Products.CMFCore.utils import getToolByName

from Products.salesforcebaseconnector.tests import sfconfig
from collective.salesforce.rsvp import config

class SFRSVPTestCase(ptc.PloneTestCase):
    
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            import collective.salesforce.rsvp
            zcml.load_config('configure.zcml',
                             collective.salesforce.rsvp)
            fiveconfigure.debug_mode = False
    
    _toCleanUp = []
    
    def _createCampaignForCleanup(self):
        # create a Campaign and append to the list of campaigns for cleanup
        campaign = dict(type='Campaign',
            Name='Fake Plone Test Case Campaign',
            IsActive=True,
        )
        res = self.sbc.create(campaign)
        sfCampaignId = res[0]['id']
        self._toCleanUp.append(sfCampaignId)
        
        # return campaign id for use by caller
        return sfCampaignId
    
    def _configureRSVPableObject(self, obj):
        # encapsulate reasonable setup of a provided
        # object that has already been said to provide
        # the ISalesforceRSVPable interface
        
        sfCampaignId = self._createCampaignForCleanup()
        
        # set rsvpable schema fields
        obj.getField('sfObjectId').set(obj, sfCampaignId)
        obj.getField('sfObjectSignupType').set(obj, 'Campaign')
        
        return sfCampaignId
    
    def _setMaxCapacityValue(self, sfCampaignId, maxCapFName, num):
        # central setting of the max capacity value
        updateData = dict(Id=sfCampaignId, 
                          type='Campaign',)
        updateData[maxCapFName] = num
        
        self.sbc.update(updateData)
    
    def _setWaitlistableStatus(self, sfCampaignId, statusFName, status):
        # central setting of the waitlistable status value value
        updateData = dict(Id=sfCampaignId, 
                          type='Campaign',)
        updateData[statusFName] = status
        
        self.sbc.update(updateData)
    
    def afterSetUp(self):
        self._toCleanUp = []
    
    def beforeTearDown(self):
        if len(self._toCleanUp):
            self.sbc.delete(self._toCleanUp)
    

@onsetup
def setup_salesforce_base_connector():
    """Install, Add, and Configure Salesforce Base Connector
       on a layer, so that we don't need to repetitively do 
       this prior to each test case run.
    """
    # aware of salesforcebaseconnector
    ztc.installProduct('salesforcebaseconnector')
    
    # get our plone site
    app = ztc.app()
    plone = app.plone
    
    # setup base connector
    plone.manage_addProduct['salesforcebaseconnector'].manage_addTool('Salesforce Base Connector', None)
    toolbox = getToolByName(plone, "portal_salesforcebaseconnector")
    toolbox.setCredentials(sfconfig.USERNAME, sfconfig.PASSWORD)
    
    # commit transaction, close connection to app ZODB
    transaction.commit()
    ztc.close(app)

ptc.setupPloneSite(products=[config.PROJECTNAME,])

# defer the configuration of Salesforce Base Connector
# until after we have a plone site
setup_salesforce_base_connector()

class SFRSVPFunctionalTestCase(ptc.FunctionalTestCase):
    """Test case class used for functional (doc-)tests
    """