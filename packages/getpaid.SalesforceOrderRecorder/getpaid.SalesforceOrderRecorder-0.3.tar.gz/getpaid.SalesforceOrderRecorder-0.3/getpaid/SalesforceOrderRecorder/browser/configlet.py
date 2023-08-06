from zope.app.form.browser import MultiCheckBoxWidget
from zope.app.form.browser import TextAreaWidget
from zope import schema
from zope.formlib.form import FormFields

from zope.interface import Interface
from zope.interface import implements
from zope.component import adapts
from zope.component import getUtility
from plone.app.controlpanel.form import ControlPanelForm
from plone.app.controlpanel.widgets import MultiCheckBoxThreeColumnWidget
from plone.fieldsets.fieldsets import FormFieldsets

from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.utils import getToolByName

class IGetPaidSalesforceOrderRecorderTypes(Interface):

    gpsor_aware_types = schema.Tuple(title=u"Recordable Content Types",
                                     description=u"Which content types should be recorded to Salesforce if they are purchased?",
                                     missing_value=tuple(),
                                     value_type=schema.Choice(vocabulary="plone.app.vocabularies.ReallyUserFriendlyTypes"),
                                     )

    gpsor_salesforce_customer_object = schema.TextLine(title=u"Salesforce Customer Object", 
                                                       description=u"This object will hold the customer, address and potentially order items if no item object is provided", 
                                                       default=None, 
                                                       required=True)

    gpsor_salesforce_item_object = schema.TextLine(title=u"Salesforce Item Object", 
                                                       description=u"This object will hold the order items. It is optional. If blank, the above object will be used, with a new SF record created for each item", 
                                                       default=None, 
                                                       required=False)

    gpsor_parent_sf_object_id = schema.TextLine(title=u"Parent Object Id", 
                                                       description=u"This will hold the id for the related parent salesforce object. This field mapping will be ignored if no object is provided for the items. (see Salesforce Item Object above)", 
                                                       default=None, 
                                                       required=False)


    gpsor_first_name = schema.TextLine(title=u"First Name", 
                                      description=u"", 
                                      default=None, 
                                      required=False)
    
    gpsor_last_name = schema.TextLine(title=u"Last Name", 
                                      description=u"", 
                                      default=None, 
                                      required=False)
    
    gpsor_phone = schema.TextLine(title=u"Phone Number", 
                                  description=u"", 
                                  default=None, 
                                  required=False)
    
    gpsor_email = schema.TextLine(title=u"Email", 
                                  description=u"", 
                                  default=None, 
                                  required=False)
    
    gpsor_contact_allowed = schema.Bool(title=u"Contact Allowed", 
                                        description=u"", 
                                        default=None, 
                                        required=False)
    
    gpsor_email_format_pref = schema.TextLine(title=u"Email Format Preference", 
                                              description=u"", 
                                              default=None, 
                                              required=False)
    
    gpsor_billing_address_name = schema.TextLine(title=u"Billing Address Name", 
                                                 description=u"", 
                                                 default=None, 
                                                 required=False)
    
    gpsor_billing_address_org = schema.TextLine(title=u"Billing Address Organization", 
                                                description=u"", 
                                                default=None, 
                                                required=False)
	
    gpsor_billing_address_street = schema.TextLine(title=u"Billing Address Street", 
                                                   description=u"", 
                                                   default=None, 
                                                   required=False)
    
    gpsor_billing_address_city = schema.TextLine(title=u"Billing Address City", 
                                                 description=u"", 
                                                 default=None, 
                                                 required=False)
    
    gpsor_billing_address_country = schema.TextLine(title=u"Billing Address Country", 
                                                    description=u"", 
                                                    default=None, 
                                                    required=False)
    
    gpsor_billing_address_state = schema.TextLine(title=u"Billing Address State", 
                                                  description=u"", 
                                                  default=None, 
                                                  required=False)
    
    gpsor_billing_address_zip = schema.TextLine(title=u"Billing Address Zip", 
                                                description=u"", 
                                                default=None, 
                                                required=False)
    
    gpsor_shipping_address_name = schema.TextLine(title=u"Shipping Address Name", 
                                                  description=u"", 
                                                  default=None, 
                                                  required=False)
    
    gpsor_shipping_address_org = schema.TextLine(title=u"Shipping Address Organization", 
                                                 description=u"", 
                                                 default=None, 
                                                 required=False)
    
    gpsor_shipping_address_street = schema.TextLine(title=u"Shipping Address Street", 
                                                    description=u"", 
                                                    default=None, 
                                                    required=False)
    
    gpsor_shipping_address_city = schema.TextLine(title=u"Shipping Address City", 
                                                  description=u"", 
                                                  default=None, 
                                                  required=False)
    
    gpsor_shipping_address_country = schema.TextLine(title=u"Shipping Address Country", 
                                                     description=u"", 
                                                     default=None, 
                                                     required=False)
    
    gpsor_shipping_address_state = schema.TextLine(title=u"Shipping Address State", 
                                                   description=u"", 
                                                   default=None, 
                                                   required=False)
    
    gpsor_shipping_address_zip = schema.TextLine(title=u"Shipping Address Zip", 
                                                 description=u"", 
                                                 default=None, 
                                                 required=False)
    
    gpsor_order_id = schema.TextLine(title=u"Order Id", 
                                     description=u"", 
                                     default=None, 
                                     required=False)
    
#Creation Date
#    gpsor_creation_date = schema.TextLine(title=u"", 
#                                              description=u"", 
#                                              default=None, 
#                                              required=False)
    
    gpsor_order_total = schema.TextLine(title=u"Order Total", 
                                        description=u"", 
                                        default=None, 
                                        required=False)
    
    gpsor_transaction_id = schema.TextLine(title=u"Transaction Id", 
                                           description=u"", 
                                           default=None, 
                                           required=False)
    
    gpsor_cc_last_4 = schema.TextLine(title=u"Cc Last 4", 
                                      description=u"", 
                                      default=None, 
                                      required=False)
    
    gpsor_shipping_service = schema.TextLine(title=u"Shipping Service", 
                                             description=u"", 
                                             default=None, 
                                             required=False)
    
    gpsor_shipping_method = schema.TextLine(title=u"Shipping Method", 
                                            description=u"", 
                                            default=None, 
                                            required=False)
    
    gpsor_shipping_weight = schema.TextLine(title=u"Shipping Weight", 
                                            description=u"", 
                                            default=None, 
                                            required=False)
    
    gpsor_shipping_cost = schema.TextLine(title=u"Shipping Cost", 
                                          description=u"", 
                                          default=None, 
                                          required=False)
    
    gpsor_item_quantity = schema.TextLine(title=u"Order Item Quantity", 
                                          description=u"", 
                                          default=None, 
                                          required=False)
    
    gpsor_item_id = schema.TextLine(title=u"Order Item Id", 
                                    description=u"", 
                                    default=None, 
                                    required=False)
    
    gpsor_item_name = schema.TextLine(title=u"Order Item Name", 
                                      description=u"", 
                                      default=None, 
                                      required=False)
    
    gpsor_product_code = schema.TextLine(title=u"Order Item Product Code", 
                                         description=u"", 
                                         default=None, 
                                         required=False)
    
    gpsor_product_sku = schema.TextLine(title=u"Order Item SKU", 
                                        description=u"", 
                                        default=None, 
                                        required=False)
    
    gpsor_item_cost = schema.TextLine(title=u"Order Item Cost", 
                                      description=u"", 
                                      default=None, 
                                      required=False)
    
    gpsor_total_item_cost = schema.TextLine(title=u"Total Order Item Cost", 
                                            description=u"", 
                                            default=None, 
                                            required=False)
    
    gpsor_item_desc = schema.TextLine(title=u"Order Item Description", 
                                      description=u"", 
                                      default=None, 
                                      required=False)
    
    gpsor_discount_code = schema.TextLine(title=u"Order Item Discount Code", 
                                          description=u"", 
                                          default=None, 
                                          required=False)
    
    gpsor_discount_title = schema.TextLine(title=u"Order Item Discount Title", 
                                           description=u"", 
                                           default=None, 
                                           required=False)
    
    gpsor_discount_total = schema.TextLine(title=u"Order Item Discount Total", 
                                           description=u"", 
                                           default=None, 
                                           required=False)
    

class GetPaidSalesforceOrderRecorderCPAdapter(SchemaAdapterBase):
    adapts(IPloneSiteRoot)
    implements(IGetPaidSalesforceOrderRecorderTypes)

    def __init__(self, context):
        super(GetPaidSalesforceOrderRecorderCPAdapter, self).__init__(context)
        portal_properties = getToolByName(context, 'portal_properties')
        self.gpsor_props = getattr(portal_properties, 'getpaidsalesforceorderrecorder')


    def set_gpsor_aware_types(self, value):
        self.gpsor_props.gpsor_aware_types = value

    def get_gpsor_aware_types(self):
        return self.gpsor_props.gpsor_aware_types
    gpsor_aware_types = property(get_gpsor_aware_types, set_gpsor_aware_types)

    def set_gpsor_salesforce_customer_object(self, value):
        self.gpsor_props.gpsor_salesforce_customer_object = value

    def get_gpsor_salesforce_customer_object(self):
        return self.gpsor_props.gpsor_salesforce_customer_object
    gpsor_salesforce_customer_object = property(get_gpsor_salesforce_customer_object, set_gpsor_salesforce_customer_object)

    def set_gpsor_salesforce_item_object(self, value):
        self.gpsor_props.gpsor_salesforce_item_object = value

    def get_gpsor_salesforce_item_object(self):
        return self.gpsor_props.gpsor_salesforce_item_object
    gpsor_salesforce_item_object = property(get_gpsor_salesforce_item_object, set_gpsor_salesforce_item_object)

    def set_gpsor_parent_sf_object_id(self, value):
        self.gpsor_props.gpsor_parent_sf_object_id = value

    def get_gpsor_parent_sf_object_id(self):
        return self.gpsor_props.gpsor_parent_sf_object_id
    gpsor_parent_sf_object_id = property(get_gpsor_parent_sf_object_id, set_gpsor_parent_sf_object_id)

    def set_gpsor_first_name(self, value):
        self.gpsor_props.gpsor_first_name = value

    def get_gpsor_first_name(self):
        return self.gpsor_props.gpsor_first_name
    gpsor_first_name = property(get_gpsor_first_name, set_gpsor_first_name)

    def set_gpsor_last_name(self, value):
        self.gpsor_props.gpsor_last_name = value

    def get_gpsor_last_name(self):
        return self.gpsor_props.gpsor_last_name
    gpsor_last_name = property(get_gpsor_last_name, set_gpsor_last_name)

    def set_gpsor_phone(self, value):
        self.gpsor_props.gpsor_phone = value

    def get_gpsor_phone(self):
        return self.gpsor_props.gpsor_phone
    gpsor_phone = property(get_gpsor_phone, set_gpsor_phone)

    def set_gpsor_email(self, value):
        self.gpsor_props.gpsor_email = value

    def get_gpsor_email(self):
        return self.gpsor_props.gpsor_email
    gpsor_email = property(get_gpsor_email, set_gpsor_email)

    def set_gpsor_contact_allowed(self, value):
        self.gpsor_props.gpsor_contact_allowed = value

    def get_gpsor_contact_allowed(self):
        return self.gpsor_props.gpsor_contact_allowed
    gpsor_contact_allowed = property(get_gpsor_contact_allowed, set_gpsor_contact_allowed)

    def set_gpsor_email_format_pref(self, value):
        self.gpsor_props.gpsor_email_format_pref = value

    def get_gpsor_email_format_pref(self):
        return self.gpsor_props.gpsor_email_format_pref
    gpsor_email_format_pref = property(get_gpsor_email_format_pref, set_gpsor_email_format_pref)

    def set_gpsor_billing_address_name(self, value):
        self.gpsor_props.gpsor_billing_address_name = value

    def get_gpsor_billing_address_name(self):
        return self.gpsor_props.gpsor_billing_address_name
    gpsor_billing_address_name = property(get_gpsor_billing_address_name, set_gpsor_billing_address_name)

    def set_gpsor_billing_address_org(self, value):
        self.gpsor_props.gpsor_billing_address_org = value

    def get_gpsor_billing_address_org(self):
        return self.gpsor_props.gpsor_billing_address_org
    gpsor_billing_address_org = property(get_gpsor_billing_address_org, set_gpsor_billing_address_org)

    def set_gpsor_billing_address_street(self, value):
        self.gpsor_props.gpsor_billing_address_street = value

    def get_gpsor_billing_address_street(self):
        return self.gpsor_props.gpsor_billing_address_street
    gpsor_billing_address_street = property(get_gpsor_billing_address_street, set_gpsor_billing_address_street)

    def set_gpsor_billing_address_city(self, value):
        self.gpsor_props.gpsor_billing_address_city = value

    def get_gpsor_billing_address_city(self):
        return self.gpsor_props.gpsor_billing_address_city
    gpsor_billing_address_city = property(get_gpsor_billing_address_city, set_gpsor_billing_address_city)

    def set_gpsor_billing_address_country(self, value):
        self.gpsor_props.gpsor_billing_address_country = value

    def get_gpsor_billing_address_country(self):
        return self.gpsor_props.gpsor_billing_address_country
    gpsor_billing_address_country = property(get_gpsor_billing_address_country, set_gpsor_billing_address_country)

    def set_gpsor_billing_address_state(self, value):
        self.gpsor_props.gpsor_billing_address_state = value

    def get_gpsor_billing_address_state(self):
        return self.gpsor_props.gpsor_billing_address_state
    gpsor_billing_address_state = property(get_gpsor_billing_address_state, set_gpsor_billing_address_state)

    def set_gpsor_billing_address_zip(self, value):
        self.gpsor_props.gpsor_billing_address_zip = value

    def get_gpsor_billing_address_zip(self):
        return self.gpsor_props.gpsor_billing_address_zip
    gpsor_billing_address_zip = property(get_gpsor_billing_address_zip, set_gpsor_billing_address_zip)

    def set_gpsor_shipping_address_name(self, value):
        self.gpsor_props.gpsor_shipping_address_name = value

    def get_gpsor_shipping_address_name(self):
        return self.gpsor_props.gpsor_shipping_address_name
    gpsor_shipping_address_name = property(get_gpsor_shipping_address_name, set_gpsor_shipping_address_name)

    def set_gpsor_shipping_address_org(self, value):
        self.gpsor_props.gpsor_shipping_address_org = value

    def get_gpsor_shipping_address_org(self):
        return self.gpsor_props.gpsor_shipping_address_org
    gpsor_shipping_address_org = property(get_gpsor_shipping_address_org, set_gpsor_shipping_address_org)

    def set_gpsor_shipping_address_street(self, value):
        self.gpsor_props.gpsor_shipping_address_street = value

    def get_gpsor_shipping_address_street(self):
        return self.gpsor_props.gpsor_shipping_address_street
    gpsor_shipping_address_street = property(get_gpsor_shipping_address_street, set_gpsor_shipping_address_street)

    def set_gpsor_shipping_address_city(self, value):
        self.gpsor_props.gpsor_shipping_address_city = value

    def get_gpsor_shipping_address_city(self):
        return self.gpsor_props.gpsor_shipping_address_city
    gpsor_shipping_address_city = property(get_gpsor_shipping_address_city, set_gpsor_shipping_address_city)

    def set_gpsor_shipping_address_country(self, value):
        self.gpsor_props.gpsor_shipping_address_country = value

    def get_gpsor_shipping_address_country(self):
        return self.gpsor_props.gpsor_shipping_address_country
    gpsor_shipping_address_country = property(get_gpsor_shipping_address_country, set_gpsor_shipping_address_country)

    def set_gpsor_shipping_address_state(self, value):
        self.gpsor_props.gpsor_shipping_address_state = value

    def get_gpsor_shipping_address_state(self):
        return self.gpsor_props.gpsor_shipping_address_state
    gpsor_shipping_address_state = property(get_gpsor_shipping_address_state, set_gpsor_shipping_address_state)

    def set_gpsor_shipping_address_zip(self, value):
        self.gpsor_props.gpsor_shipping_address_zip = value

    def get_gpsor_shipping_address_zip(self):
        return self.gpsor_props.gpsor_shipping_address_zip
    gpsor_shipping_address_zip = property(get_gpsor_shipping_address_zip, set_gpsor_shipping_address_zip)

    def set_gpsor_order_id(self, value):
        self.gpsor_props.gpsor_order_id = value

    def get_gpsor_order_id(self):
        return self.gpsor_props.gpsor_order_id
    gpsor_order_id = property(get_gpsor_order_id, set_gpsor_order_id)

    def set_gpsor_creation_date(self, value):
        self.gpsor_props.gpsor_creation_date = value

    def get_gpsor_creation_date(self):
        return self.gpsor_props.gpsor_creation_date
    gpsor_creation_date = property(get_gpsor_creation_date, set_gpsor_creation_date)

    def set_gpsor_order_total(self, value):
        self.gpsor_props.gpsor_order_total = value

    def get_gpsor_order_total(self):
        return self.gpsor_props.gpsor_order_total
    gpsor_order_total = property(get_gpsor_order_total, set_gpsor_order_total)

    def set_gpsor_transaction_id(self, value):
        self.gpsor_props.gpsor_transaction_id = value

    def get_gpsor_transaction_id(self):
        return self.gpsor_props.gpsor_transaction_id
    gpsor_transaction_id = property(get_gpsor_transaction_id, set_gpsor_transaction_id)

    def set_gpsor_cc_last_4(self, value):
        self.gpsor_props.gpsor_cc_last_4 = value

    def get_gpsor_cc_last_4(self):
        return self.gpsor_props.gpsor_cc_last_4
    gpsor_cc_last_4 = property(get_gpsor_cc_last_4, set_gpsor_cc_last_4)

    def set_gpsor_shipping_service(self, value):
        self.gpsor_props.gpsor_shipping_service = value

    def get_gpsor_shipping_service(self):
        return self.gpsor_props.gpsor_shipping_service
    gpsor_shipping_service = property(get_gpsor_shipping_service, set_gpsor_shipping_service)

    def set_gpsor_shipping_method(self, value):
        self.gpsor_props.gpsor_shipping_method = value

    def get_gpsor_shipping_method(self):
        return self.gpsor_props.gpsor_shipping_method
    gpsor_shipping_method = property(get_gpsor_shipping_method, set_gpsor_shipping_method)

    def set_gpsor_shipping_weight(self, value):
        self.gpsor_props.gpsor_shipping_weight = value

    def get_gpsor_shipping_weight(self):
        return self.gpsor_props.gpsor_shipping_weight
    gpsor_shipping_weight = property(get_gpsor_shipping_weight, set_gpsor_shipping_weight)

    def set_gpsor_shipping_cost(self, value):
        self.gpsor_props.gpsor_shipping_cost = value

    def get_gpsor_shipping_cost(self):
        return self.gpsor_props.gpsor_shipping_cost
    gpsor_shipping_cost = property(get_gpsor_shipping_cost, set_gpsor_shipping_cost)

    def set_gpsor_item_quantity(self, value):
        self.gpsor_props.gpsor_item_quantity = value

    def get_gpsor_item_quantity(self):
        return self.gpsor_props.gpsor_item_quantity
    gpsor_item_quantity = property(get_gpsor_item_quantity, set_gpsor_item_quantity)

    def set_gpsor_item_id(self, value):
        self.gpsor_props.gpsor_item_id = value

    def get_gpsor_item_id(self):
        return self.gpsor_props.gpsor_item_id
    gpsor_item_id = property(get_gpsor_item_id, set_gpsor_item_id)

    def set_gpsor_item_name(self, value):
        self.gpsor_props.gpsor_item_name = value

    def get_gpsor_item_name(self):
        return self.gpsor_props.gpsor_item_name
    gpsor_item_name = property(get_gpsor_item_name, set_gpsor_item_name)

    def set_gpsor_product_code(self, value):
        self.gpsor_props.gpsor_product_code = value

    def get_gpsor_product_code(self):
        return self.gpsor_props.gpsor_product_code
    gpsor_product_code = property(get_gpsor_product_code, set_gpsor_product_code)

    def set_gpsor_product_sku(self, value):
        self.gpsor_props.gpsor_product_sku = value

    def get_gpsor_product_sku(self):
        return self.gpsor_props.gpsor_product_sku
    gpsor_product_sku = property(get_gpsor_product_sku, set_gpsor_product_sku)

    def set_gpsor_item_cost(self, value):
        self.gpsor_props.gpsor_item_cost = value

    def get_gpsor_item_cost(self):
        return self.gpsor_props.gpsor_item_cost
    gpsor_item_cost = property(get_gpsor_item_cost, set_gpsor_item_cost)

    def set_gpsor_total_item_cost(self, value):
        self.gpsor_props.gpsor_total_item_cost = value

    def get_gpsor_total_item_cost(self):
        return self.gpsor_props.gpsor_total_item_cost
    gpsor_total_item_cost = property(get_gpsor_total_item_cost, set_gpsor_total_item_cost)

    def set_gpsor_item_desc(self, value):
        self.gpsor_props.gpsor_item_desc = value

    def get_gpsor_item_desc(self):
        return self.gpsor_props.gpsor_item_desc
    gpsor_item_desc = property(get_gpsor_item_desc, set_gpsor_item_desc)

    def set_gpsor_discount_code(self, value):
        self.gpsor_props.gpsor_discount_code = value

    def get_gpsor_discount_code(self):
        return self.gpsor_props.gpsor_discount_code
    gpsor_discount_code = property(get_gpsor_discount_code, set_gpsor_discount_code)

    def set_gpsor_discount_title(self, value):
        self.gpsor_props.gpsor_discount_title = value

    def get_gpsor_discount_title(self):
        return self.gpsor_props.gpsor_discount_title
    gpsor_discount_title = property(get_gpsor_discount_title, set_gpsor_discount_title)

    def set_gpsor_discount_total(self, value):
        self.gpsor_props.gpsor_discount_total = value

    def get_gpsor_discount_total(self):
        return self.gpsor_props.gpsor_discount_total
    gpsor_discount_total = property(get_gpsor_discount_total, set_gpsor_discount_total)


fs_gpsortypes = FormFieldsets(IGetPaidSalesforceOrderRecorderTypes)
fs_gpsortypes.id = 'gpsortypes'
fs_gpsortypes.label = u'Types Settings'

class PHMultiCheckBoxWidget(MultiCheckBoxWidget):

    def __init__(self, field, request):
        """Initialize the widget."""
        super(MultiCheckBoxWidget, self).__init__(field,
            field.value_type.vocabulary, request)

class GetPaidSalesforceOrderRecorderCP(ControlPanelForm):

    form_fields = FormFieldsets(fs_gpsortypes)

    # title of the page
    label = "GetPaid Salesforce Order Recorder Settings"

    # explanatory text
    description = u"""Map a content type to an adapter"""

    # fieldset legend
    form_name = "GetPaid Salesforce Order Recorder Settings"
    form_fields['gpsor_aware_types'].custom_widget = MultiCheckBoxThreeColumnWidget
