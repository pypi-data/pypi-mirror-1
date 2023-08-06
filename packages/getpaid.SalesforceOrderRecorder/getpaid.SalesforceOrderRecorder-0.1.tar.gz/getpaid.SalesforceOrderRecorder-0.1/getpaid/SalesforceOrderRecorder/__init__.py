from AccessControl import ModuleSecurityInfo
from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory

from getpaid.SalesforceOrderRecorder.config import PROJECTNAME, GLOBALS


# Import "PloneFormGenMessageFactory as _" to create message ids
# in the ploneformgen domain
# Zope 3.1-style messagefactory module
# BBB: Zope 2.8 / Zope X3.0
try:
    from zope.i18nmessageid import MessageFactory
except ImportError:
    from messagefactory_ import SalesforceOrderRecorderMessageFactory
else:
    SalesforceOrderRecorderMessageFactory = MessageFactory('getpaidsalesforceorderrecorder')

# Check for Plone versions
try:
    from Products.CMFPlone.migrations import v2_5
except ImportError:
    HAS_PLONE25 = False
else:
    HAS_PLONE25 = True
try:
    from Products.CMFPlone.migrations import v3_0
except ImportError:
    HAS_PLONE30 = False
else:
    HAS_PLONE30 = True
