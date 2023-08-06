"""

Annotation Property Storage and Site Configuration Settings

$Id: preferences.py 1720 2008-08-07 02:02:44Z rs_alves@aeiou.pt $
"""

from getpaid.core.options import PersistentBag
from zope import component
import interfaces

def ConfigurationPreferences( site ):

    settings = component.queryUtility(interfaces.IGetPaidSalesforceOrderRecorderManagementOptions)

    # store access to the site, because our vocabularies get the setting as context
    # and want to access portal tools to construct various vocabs
    settings._v_site = site
    return settings

_OrderRecorderSettings = PersistentBag.makeclass( interfaces.IGetPaidSalesforceOrderRecorderManagementOptions )

class OrderRecorderSettings( _OrderRecorderSettings ):

    _v_site = None
    
    @property
    def context( self ):
        return self._v_site

    def manage_fixupOwnershipAfterAdd( self ): pass


