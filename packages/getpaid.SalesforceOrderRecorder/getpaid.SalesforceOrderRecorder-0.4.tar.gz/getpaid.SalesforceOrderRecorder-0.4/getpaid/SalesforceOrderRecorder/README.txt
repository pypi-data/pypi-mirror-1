GetPaid Salesforce Order Recorder
============================================

Overview
========

--- Need to flesh this out ---

Allows for the storage of getpaid orders to salesforce.  Must be configured in the admin console before it will work.  User must specify the content type they are interested in and give instructions on how to map it to salesforce.  If that content type appears in a charged order the entire order is saved to salesforce (even if there are other content types)

Dependencies
============

Depends upon the beatbox library >= 0.9.1.1, which is a Python wrapper to the
Salesforce.com API (version 7.0).  You must have a Salesforce.com account
that provides API access.

To download and install beatbox, please visit::

 http://code.google.com/p/salesforce-beatbox/

SalesforceBaseConnector >= 1.0a3. See 
http://plone.org/products/salesforcebaseconnector

 
Credits
=======

- Rob LaRubbio <rob --AT-- onenw --DOT-- org>

The Plone & Salesforce crew in Seattle and Portland for their work on
Salesforce PFG Adapter:

- Jon Baldivieso <jonb --AT-- onenw --DOT-- org>
- Andrew Burkhalter <andrewb --AT-- onenw --DOT-- org>
- David Glick <davidglick --AT-- onenw --DOT-- org> 

Jesse Snyder and NPower Seattle for the foundation of code that has become
Salesforce Base Connector
 
Simon Fell for providing the beatbox Python wrapper to the Salesforce.com API
 
Salesforce.com Foundation and Enfold Systems for their gift and work on 
beatbox (see: http://gokubi.com/archives/onenorthwest-gets-grant-from-salesforcecom-to-integrate-with-plone)

See the CHANGES.txt file for the growing list of people who helped
with particular features or bugs.


License
=======

Distributed under the GPL.

See LICENSE.txt and LICENSE.GPL for details.


