import zope.interface

class IPayPal(zope.interface.Interface):
    """Utility to provide paypal API"""

class IPayPalDataProvider(zope.interface.Interface):
    """Interface providing needed paypal account data"""
    username = zope.interface.Attribute('PayPal API user name')
    password = zope.interface.Attribute('PayPal API password')
    signature = zope.interface.Attribute('PayPal API signature')
    version = zope.interface.Attribute('PayPal API Version')
    currency = zope.interface.Attribute('PayPal API Currency')
    api_endpoint = zope.interface.Attribute('PayPal API Endpoint')
    paypal_url = zope.interface.Attribute('PayPal API URL')
    callback_url = zope.interface.Attribute('PayPal API Callback URL')
    callback_cancel_url = zope.interface.Attribute('PayPal API Cancel URL')

