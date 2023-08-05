#!/usr/bin/env python

# PayPal python NVP API wrapper class.
# This is a sample to help others get started on working
# with the PayPal NVP API in Python. 
# This is not a complete reference! Be sure to understand
# what this class is doing before you try it on production servers!
# ...use at your own peril.

## see https://www.paypal.com/IntegrationCenter/ic_nvp.html
## and
## https://www.paypal.com/en_US/ebook/PP_NVPAPI_DeveloperGuide/index.html
## for more information.

# by Mike Atlas / LowSingle.com / MassWrestling.com, September 2007
# No License Expressed. Feel free to distribute, modify, 
#  and use in any open or closed source project without credit to the author

# Example usage: ===============
#   paypal = PayPal()
#   pp_token = paypal.SetExpressCheckout(100)
#   express_token = paypal.GetExpressCheckoutDetails(pp_token)
#   url= paypal.PAYPAL_URL + express_token
#   HttpResponseRedirect(url) ## django specific http redirect call for payment


import urllib, md5, datetime
import zope.interface
import gocept.paypal.interfaces

class PayPal(object):
    """ #PayPal utility class"""
    zope.interface.implements(gocept.paypal.interfaces.IPayPal)
    signature_values = {}
    API_ENDPOINT = ""
    PAYPAL_URL = ""

    def __init__(self):
        pass

    def _update_values(self):
        """ Sandbox values """
        dataprovider = gocept.paypal.interfaces.IPayPalDataProvider(self)
        self.signature_values = {
            'USER' : dataprovider.username,
            'PWD' : dataprovider.password,
            'SIGNATURE' : dataprovider.signature,
            'VERSION' : dataprovider.version,
        }
        self.API_ENDPOINT = dataprovider.api_endpoint
        self.PAYPAL_URL = dataprovider.paypal_url
        self.signature = urllib.urlencode(self.signature_values) + "&"

    # API METHODS
    def SetExpressCheckout(self, amount, callback_url, callback_cancel_url):
        self._update_values()
        params = {
            'METHOD' : "SetExpressCheckout",
            'NOSHIPPING' : 1,
            'PAYMENTACTION' : 'Authorization',
            'RETURNURL' : callback_url,
            'CANCELURL' : callback_cancel_url,
            'AMT' : amount,
        }

        params_string = self.signature + urllib.urlencode(params)
        response = urllib.urlopen(self.API_ENDPOINT, params_string).read()
        params = response.split('&')
        for param in params:
            if param.startswith('TOKEN='):
                return param[6:].strip()
        raise ValueError('There was no TOKEN returned: %s' % params)

    def GetExpressCheckoutDetails(self, token, callback_url,
                                                    callback_cancel_url):
        self._update_values()
        params = {
            'METHOD' : "GetExpressCheckoutDetails",
            'RETURNURL' : callback_url,
            'CANCELURL' : callback_cancel_url,
            'TOKEN' : token,
        }
        params_string = self.signature + urllib.urlencode(params)
        response = urllib.urlopen(self.API_ENDPOINT, params_string).read()
        response_tokens = {}
        for token in response.split('&'):
            response_tokens[token.split("=")[0]] = token.split("=")[1]
        for key in response_tokens.keys():
            response_tokens[key] = urllib.unquote(response_tokens[key])
        return response_tokens

    def DoExpressCheckoutPayment(self, token, payer_id, amt, callback_url,
                                                      callback_cancel_url):
        self._update_values()
        params = {
            'METHOD' : "DoExpressCheckoutPayment",
            'PAYMENTACTION' : 'Sale',
            'RETURNURL' : callback_url,
            'CANCELURL' : callback_cancel_url,
            'TOKEN' : token,
            'AMT' : amt,
            'PAYERID' : payer_id,
        }
        params_string = self.signature + urllib.urlencode(params)
        response = urllib.urlopen(self.API_ENDPOINT, params_string).read()
        response_tokens = {}
        for token in response.split('&'):
            response_tokens[token.split("=")[0]] = token.split("=")[1]
        for key in response_tokens.keys():
            response_tokens[key] = urllib.unquote(response_tokens[key])
        return response_tokens

    def GetTransactionDetails(self, tx_id):
        self._update_values()
        params = {
            'METHOD' : "GetTransactionDetails", 
            'TRANSACTIONID' : tx_id,
        }
        params_string = self.signature + urllib.urlencode(params)
        response = urllib.urlopen(self.API_ENDPOINT, params_string).read()
        response_tokens = {}
        for token in response.split('&'):
            response_tokens[token.split("=")[0]] = token.split("=")[1]
        for key in response_tokens.keys():
            response_tokens[key] = urllib.unquote(response_tokens[key])
        response_tokens['TOKEN'] = response_tokens['TOKEN'][3:]
        return response_tokens

    def MassPay(self, email, amt, note, email_subject):
        self._update_values()
        unique_id = str(md5.new(str(datetime.datetime.now())).hexdigest())
        params = {
            'METHOD' : "MassPay",
            'RECEIVERTYPE' : "EmailAddress",
            'L_AMT0' : amt,
            'CURRENCYCODE' : 'USD',
            'L_EMAIL0' : email,
            'L_UNIQUE0' : unique_id,
            'L_NOTE0' : note,
            'EMAILSUBJECT': email_subject,
        }
        params_string = self.signature + urllib.urlencode(params)
        response = urllib.urlopen(self.API_ENDPOINT, params_string).read()
        response_tokens = {}
        for token in response.split('&'):
            response_tokens[token.split("=")[0]] = token.split("=")[1]
        for key in response_tokens.keys():
                response_tokens[key] = urllib.unquote(response_tokens[key])
        response_tokens['unique_id'] = unique_id
        return response_tokens

    def DoDirectPayment(self, amt, ipaddress, acct, expdate, cvv2,
                        firstname, lastname, cctype, street, city, state,
                        zipcode, callback_url, callback_cancel_url):
        self._update_values()
        params = {
            'METHOD' : "DoDirectPayment",
            'PAYMENTACTION' : 'Sale',
            'AMT' : amt,
            'IPADDRESS' : ipaddress,
            'ACCT': acct,
            'EXPDATE' : expdate,
            'CVV2' : cvv2,
            'FIRSTNAME' : firstname,
            'LASTNAME': lastname,
            'CREDITCARDTYPE': cctype,
            'STREET': street,
            'CITY': city,
            'STATE': state,
            'ZIP':zipcode,
            'COUNTRY' : 'United States',
            'COUNTRYCODE': 'US',
            'RETURNURL' : callback_url,
            'CANCELURL' : callback_cancel_url,
            'L_DESC0' : "Desc: ",
            'L_NAME0' : "Name: ",
        }
        params_string = self.signature + urllib.urlencode(params)
        response = urllib.urlopen(self.API_ENDPOINT, params_string).read()
        response_tokens = {}
        for token in response.split('&'):
            response_tokens[token.split("=")[0]] = token.split("=")[1]
        for key in response_tokens.keys():
            response_tokens[key] = urllib.unquote(response_tokens[key])
        return response_tokens
