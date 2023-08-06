""" 
    A plugin for GetPaid that saves orders
    to Salesforce.com after it is charged
"""

__author__  = ''
__docformat__ = 'plaintext'

# Python imorts
import logging

from Products.CMFCore.utils import getToolByName

from getpaid.SalesforceOrderRecorder import SalesforceOrderRecorderMessageFactory as _

# Get Paid events
from getpaid.core.interfaces import workflow_states, IShoppingCartUtility, IShippableOrder, IShippingRateService, IShippableLineItem
from zope.app.component.hooks import getSite

logger = logging.getLogger("SalesforceOrderRecorder")

def handleOrderWorkflowTransition( order, event ):

    logger.info("handleOrderWorkflowTransition: %s, %s" % (order.finance_state, event.destination));

    # Only save the order if it has moved into the charged state
    # and the order was placed through PloneFormGen and the adapter is enabled
    if order.finance_state == event.destination and event.destination == workflow_states.order.finance.CHARGED:

        try:
            executeAdapter(order)
        except ConflictError:
            raise
        except Exception, e:
            # I catch everything since any uncaught exception here
            # will prevent the order from moving to charged
            logger.error("Exception saving order %s to salesforce: %s" % (order.order_id, e))
        except:
            logger.error("Unknown Exception saving order %s to salesforce" % (order.order_id))


def executeAdapter(order):
    portal_properties = getToolByName(getSite(), 'portal_properties')
    props = getattr(portal_properties, 'getpaidsalesforceorderrecorder')
    refCat = getToolByName( getSite(), 'reference_catalog')
    salesforce = getToolByName(getSite(), 'portal_salesforcebaseconnector')

    # Get the content types that I will map
    itemTypes = props.gpsor_aware_types

    # Loop over the items and see if any are mappable
    itemList = []
    for item in order.shopping_cart.items():
        payable = refCat.lookupObject( item[0] )
        itemType = payable.portal_type

        if itemType in itemTypes:
            itemList.append(item)

    # If there is something in my list then there is at least
    # one item to record
    if len(itemList):
        customerSObject = props.gpsor_salesforce_customer_object
        itemSObject = props.gpsor_salesforce_item_object

        if itemSObject is None or itemSObject == "" or itemSObject == customerSObject:
            # Loop over the items mapping customer and item to same 
            # SFObject I will have multiple SF Objects
            sObject = []
                
            # Loop over cart items creating an sObject for each
            for item in order.shopping_cart.items():
                obj = dict(type=customerSObject)
                sObject.append(obj)

                _mapOrderFields(order, obj, props)
                _mapItemFields(item[1], obj, props)

            results = salesforce.create(sObject)
            for result in results:
                if result['success']:
                    logger.info("Successfully created new %s %s for order %s in Salesforce" % \
                                    (sObject[0]['type'], result['id'], order.order_id))
                else:
                    for error in result['errors']:
                        logger.error('Failed to create new %s for order %s in Salesforce: %s' % \
                                         (sObject[0]['type'], order.order_id, error['message']))
                
        else:
            # Loop over the items mapping customer and item to same SFObject
            # I will have multiple SF Objects

            # first create the customer obejct in SF
            obj = dict(type=customerSObject)

            # I kind of think it's a hack to pass None for the item
            # the method expects it, but in this case will not use
            # it since I'm passing the customer field map.
            _mapOrderFields(order, obj, props)

            results = salesforce.create(obj)
            if results[0]['success']:
                logger.info("Successfully created new %s %s for order %s in Salesforce" % \
                                (obj['type'], results[0]['id'], order.order_id))

                obj['id'] = results[0]['id']

                # Loop over cart items creating an sObject for each
                sObjects = []
                for item in order.shopping_cart.items():
                    itemObj = dict(type=itemSObject)
                    sObjects.append(itemObj)

                    _mapItemFields(item[1], itemObj, props, obj['id'])

                results = salesforce.create(sObjects)
                for result in results:
                    if result['success']:
                        logger.info("Successfully created new %s %s in Salesforce" % \
                                        (sObjects[0]['type'], result['id']))
                    else:
                        for error in result['errors']:
                            logger.error('Failed to create new %s for order %s in Salesforce: %s' % \
                                             (sObjects[0]['type'], order.order_id, error['message']))

            else:
                for error in results['errors']:
                    logger.error('Failed to create new %s for order %s in Salesforce: %s' % \
                                     (obj['type'], order.order_id, error['message']))


def _mapOrderFields(order, sfObject, props):
    if props.gpsor_first_name:
        fullName = order.contact_information.name
        firstName = fullName.split(' ', 1)[0]

        if firstName is not None:
            sfObject[props.gpsor_first_name] = firstName
    
    if props.gpsor_last_name:
        fullName = order.contact_information.name
        lastName = fullName.split(' ', 1)[1]

        if lastName is not None:
            sfObject[props.gpsor_last_name] = lastName

    if props.gpsor_phone:
        if order.contact_information.phone_number is not None:
            sfObject[props.gpsor_phone] = order.contact_information.phone_number
            
    if props.gpsor_email:
        if order.contact_information.email is not None:
            sfObject[props.gpsor_email] = order.contact_information.email

    if props.gpsor_contact_allowed:
        if order.contact_information.marketing_preference is not None:
            sfObject[props.gpsor_contact_allowed] = order.contact_information.marketing_preference

    if props.gpsor_email_format_pref:
        if order.contact_information.email_html_format is not None:
            sfObject[props.gpsor_email_format_pref] = order.contact_information.email_html_format

    if props.gpsor_billing_address_name:
        if order.billing_address.bill_name is not None:
            sfObject[props.gpsor_billing_address_name] = order.billing_address.bill_name

    if props.gpsor_billing_address_org:
        if order.billing_address.bill_organization is not None:
            sfObject[props.gpsor_billing_address_org] = order.billing_address.bill_organization

    if props.gpsor_billing_address_street:
        line_1 = order.billing_address.bill_first_line
        line_2 = order.billing_address.bill_second_line

        if line_2 is None:
            value = line_1
        else:
            value = "\n".join((line_1, line_2))

        if value is not None:
            sfObject[props.gpsor_billing_address_street] = value

    if props.gpsor_billing_address_city:
        if order.billing_address.bill_city is not None:
            sfObject[props.gpsor_billing_address_city] = order.billing_address.bill_city

    if props.gpsor_billing_address_country:
        if order.billing_address.bill_country is not None:
            sfObject[props.gpsor_billing_address_country] = order.billing_address.bill_country

    if props.gpsor_billing_address_state:
        if order.billing_address.bill_state is not None:
            sfObject[props.gpsor_billing_address_state] = order.billing_address.bill_state

    if props.gpsor_billing_address_zip:
        if order.billing_address.bill_postal_code is not None:
            sfObject[props.gpsor_billing_address_zip] = order.billing_address.bill_postal_code

    if props.gpsor_shipping_address_name:
        if order.shipping_address.ship_same_billing:
            value = order.billing_address.bill_name
        else:
            value = order.shipping_address.ship_name

        if value is not None:
            sfObject[props.gpsor_shipping_address_name] = value

    if props.gpsor_shipping_address_org:
        if order.shipping_address.ship_same_billing:
            value = order.billing_address.bill_organization
        else:
            value = order.shipping_address.ship_organization

        if value is not None:
            sfObject[props.gpsor_shipping_address_org] = value

    if props.gpsor_shipping_address_street:
        if order.shipping_address.ship_same_billing:
            line_1 = order.billing_address.bill_first_line
            line_2 = order.billing_address.bill_second_line
        else:
            line_1 = order.shipping_address.ship_first_line
            line_2 = order.shipping_address.ship_second_line

        if line_2 is None:
            value = line_1
        else:
            value = "\n".join((line_1, line_2))

        if value is not None:
            sfObject[props.gpsor_shipping_address_street] = value

    if props.gpsor_shipping_address_city:
        if order.shipping_address.ship_same_billing:
            value = order.billing_address.bill_city
        else:
            value = order.shipping_address.ship_city

        if value is not None:
            sfObject[props.gpsor_shipping_address_city] = value

    if props.gpsor_shipping_address_country:
        if order.shipping_address.ship_same_billing:
            value = order.billing_address.bill_country
        else:
            value = order.shipping_address.ship_country

        if value is not None:
            sfObject[props.gpsor_shipping_address_country] = value

    if props.gpsor_shipping_address_state:
        if order.shipping_address.ship_same_billing:
            value = order.billing_address.bill_state
        else:
            value = order.shipping_address.ship_state

        if value is not None:
            sfObject[props.gpsor_shipping_address_state] = value

    if props.gpsor_shipping_address_zip:
        if order.shipping_address.ship_same_billing:
            value = order.billing_address.bill_postal_code
        else:
            value = order.shipping_address.ship_postal_code

        if value is not None:
            sfObject[props.gpsor_shipping_address_zip] = value

    if props.gpsor_order_id:
        if order.order_id is not None:
                    sfObject[props.gpsor_order_id] = order.order_id

#    if props.gpsor_creation_date:
#        sfObject[props.gpsor_creation_date] = 

    if props.gpsor_order_total:
        if order.getTotalPrice() is not None:
            sfObject[props.gpsor_order_total] = order.getTotalPrice()

    if props.gpsor_transaction_id:
        if order.processor_order_id is not None:
            sfObject[props.gpsor_transaction_id] = order.processor_order_id

    if props.gpsor_cc_last_4:
        if order.user_payment_info_last4 is not None:
            sfObject[props.gpsor_cc_last_4] = order.user_payment_info_last4

    if props.gpsor_shipping_service:
        if getShippingService(order) is not None:
            sfObject[props.gpsor_shipping_service] = getShippingService(order)

    if props.gpsor_shipping_method:
        if getShippingMethod(order) is not None:
            sfObject[props.gpsor_shipping_method] = getShippingMethod(order)

    if props.gpsor_shipping_weight:
        if getShipmentWeight(order) is not None:
            sfObject[props.gpsor_shipping_weight] = getShipmentWeight(order)

    if props.gpsor_shipping_cost:
        if order.getShippingCost() is not None:
            sfObject[props.gpsor_shipping_cost] = order.getShippingCost()

def _mapItemFields(item, sfObject, props, parentSFObjectId=None):

    if parentSFObjectId and props.gpsor_parent_sf_object_id:
        sfObject[props.gpsor_parent_sf_object_id] = parentSFObjectId

    if props.gpsor_item_quantity:
        if item.quantity is not None:
            sfObject[props.gpsor_item_quantity] = item.quantity

    if props.gpsor_item_id:
        if order.shopping_cart.items.item_id is not None:
            sfObject[props.gpsor_item_id] = order.shopping_cart.items.item_id

    if props.gpsor_item_name:
        if item.name is not None:
            sfObject[props.gpsor_item_name] = item.name

    if props.gpsor_product_code:
        if item.product_code is not None:
            sfObject[props.gpsor_product_code] = item.product_code

    if props.gpsor_product_sku:
        if item.sku is not None:
            sfObject[props.gpsor_product_sku] = item.sku

    if props.gpsor_item_cost:
        if item.cost is not None:
            sfObject[props.gpsor_item_cost] = item.cost

    if props.gpsor_total_item_cost:
        totalCost = item.cost * item.quantity
        if totalCost is not None:
            sfObject[props.gpsor_total_item_cost] = totalCost

    if props.gpsor_item_desc:
        if item.description is not None:
            sfObject[props.gpsor_item_desc] = item.description

    if props.gpsor_discount_code:
        value = ""
        annotation = IAnnotations(item[1])
        if "getpaid.discount.code" in annotation:
            value = annotation["getpaid.discount.code"]

            if value is not None:
                sfObject[props.gpsor_discount_code] = value

    if props.gpsor_discount_title:
        value = ""
        annotation = IAnnotations(item[1])
        if "getpaid.discount.code.title" in annotation:
            value = annotation["getpaid.discount.code.title"]

            if value is not None:
                sfObject[props.gpsor_discount_title] = value

    if props.gpsor_discount_total:
        value = ""
        annotation = IAnnotations(item[1])
        if "getpaid.discount.code.discount" in annotation:
            value = annotation["getpaid.discount.code.discount"]

            if value is not None:
                sfObject[props.gpsor_discount_total] = value


def getShippingService(order):
    if not hasattr(order,"shipping_service"):
        return None
    infos = order.shipping_service
    if infos:
        return infos

def getShippingMethod(order):
    # check the traversable wrrapper
    if not IShippableOrder.providedBy( order ):
        return None
    
    service = zope.component.queryUtility( IShippingRateService,
                                           order.shipping_service )
    
    # play nice if the a shipping method is removed from the store
    if not service: 
        return None
        
    return service.getMethodName( order.shipping_method )
    
def getShipmentWeight(order):
    """
    Lets return the weight in lbs for the moment
    """
    # check the traversable wrrapper
    if not IShippableOrder.providedBy( order ):
        return None

    totalShipmentWeight = 0
    for eachProduct in order.shopping_cart.values():
        if IShippableLineItem.providedBy( eachProduct ):
            weightValue = eachProduct.weight * eachProduct.quantity
            totalShipmentWeight += weightValue
    return totalShipmentWeight
