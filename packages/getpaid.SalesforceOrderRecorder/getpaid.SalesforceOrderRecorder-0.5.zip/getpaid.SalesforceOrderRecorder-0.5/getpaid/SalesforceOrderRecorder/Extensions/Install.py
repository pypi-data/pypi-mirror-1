from getpaid.SalesforceOrderRecorder import preferences
from getpaid.SalesforceOrderRecorder.config import PROJECTNAME
from getpaid.SalesforceOrderRecorder import HAS_PLONE25, HAS_PLONE30
from getpaid.SalesforceOrderRecorder.interfaces import IGetPaidSalesforceOrderRecorderManagementOptions

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ManagePortal
from Products.CMFPlone.utils import versionTupleFromString

from StringIO import StringIO

DEPENDENCIES = ('Products.salesforcebaseconnector',)

def install(self):
    out = StringIO()
    
    print >> out, "Installing dependency products"
    portal_qi = getToolByName(self, 'portal_quickinstaller')
    for depend in DEPENDENCIES:
        if portal_qi.isProductInstallable(depend) and not portal_qi.isProductInstalled(depend):
            portal_qi.installProduct(depend)
    
    # run our profile first.  among other things, it sets up our local utility:
    # the Pigeonholizer!!!
    portal_setup.runAllImportStepsFromProfile('profile-getpaid.SalesforceOrderRecorder:default', purge_old=False)
    portal_quickinstaller.notifyInstalled("GetpaidSalesforceOrderRecorder")

    # Set up the settings configlet
    portal = getToolByName( self, 'portal_url').getPortalObject()
    sm = portal.getSiteManager()

    return out.getvalue()


def uninstall(self):
    out = StringIO()
    
    if not reinstall:
        # remove icon from portal_actionicons
        icons = getToolByName(self, 'portal_actionicons')
        if 'getpaidsalesforceorderrecorder' in [a.getActionId().lower() for a in icons.listActionIcons()]:
            icons.removeActionIcon(category='controlpanel', action_id='getpaidsalesforceorderrecorder')

        # remove control panel registration
        ctl = getToolByName(self, 'portal_controlpanel')
        if 'getpaidsalesforceorderrecorder' in [a.getId() for a in ctl.listActions()]:
            ctl.unregisterConfiglet('getpaidsalesforceorderrecorder')

        # remove property sheet
        props = getToolByName(self, 'portal_properties')
        if 'getpaidsalesforceorderrecorder' in props:
            props._delObject('getpaidsalesforceorderrecorder')
        
    print >> out, "\nSuccessfully uninstalled %s." % PROJECTNAME

    return out.getvalue()
