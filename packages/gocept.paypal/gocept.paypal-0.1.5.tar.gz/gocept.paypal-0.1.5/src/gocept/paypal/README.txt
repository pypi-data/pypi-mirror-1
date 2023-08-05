===============
 gocept.paypal
===============

>>> from zc.testbrowser.browser import Browser
>>> browser = Browser()

Testing the default paypal shopping flow
----------------------------------------

>>> browser.mech_browser.set_handle_robots(False)
>>> import zope.component
>>> import gocept.paypal.paypal
>>> import gocept.paypal.interfaces
>>> import gocept.paypal.config_tests
>>> class PPData(object):
...     zope.component.adapts(gocept.paypal.interfaces.IPayPal)
...     zope.interface.implements(gocept.paypal.interfaces.IPayPalDataProvider)
...
...     username = gocept.paypal.config_tests.USERNAME
...     password = gocept.paypal.config_tests.PASSWORD
...     signature = gocept.paypal.config_tests.SIGNATURE
...     version = gocept.paypal.config_tests.VERSION
...     api_endpoint = gocept.paypal.config_tests.API_ENDPOINT
...     paypal_url = gocept.paypal.config_tests.PAYPAL_URL
...
...     def __init__(self, context):
...         self.context = context
...
...
>>> gsm = zope.component.getGlobalSiteManager()
>>> gsm.registerAdapter(PPData)
>>> callback_url = gocept.paypal.config_tests.CALLBACK_URL
>>> callback_cancel_url = gocept.paypal.config_tests.CALLBACK_CANCEL_URL

Login to the paypal developer site

>>> browser.open('https://developer.paypal.com/')
>>> browser.getControl(name='login_email').value = gocept.paypal.config_tests.DEVELOPER_LOGIN
>>> browser.getControl(name='login_password').value = gocept.paypal.config_tests.DEVELOPER_PASSWORD
>>> browser.getControl(name='submit').click()
>>> 'Now loading,' in browser.contents
True


>>> paypal = gocept.paypal.paypal.PayPal()

We now make a new payment request with the amount €1,00 and get back a token from the API.

>>> amt = 1
>>> token = paypal.SetExpressCheckout(amt, callback_url, callback_cancel_url)

Call the paypal site with the token as an argument, login and click continue.

>>> url = '%s%s' % (gocept.paypal.config_tests.PAYPAL_URL, token)
>>> browser.open(url)
>>> browser.getControl(name='login_email').value = gocept.paypal.config_tests.BUYER_EMAIL
>>> browser.getControl(name='login_password').value = gocept.paypal.config_tests.BUYER_PASSWORD
>>> browser.getControl(name='login.x').click()
>>> browser.getControl(name='continue.x').click()
>>> token = browser.contents
>>> express_tokens = paypal.GetExpressCheckoutDetails(token, callback_url, callback_cancel_url)
>>> express_tokens['ACK'] == 'Success'
True

Now we call the next step of the payment process.

>>> payerid = express_tokens['PAYERID']
>>> pay_tokens = paypal.DoExpressCheckoutPayment(express_tokens['TOKEN'], payerid, amt, callback_url, callback_cancel_url)
>>> pay_tokens['ACK'] == 'Success'
True

Testing the direct payment process
----------------------------------

>>> status = paypal.DoDirectPayment(
...                 amt,
...                 '192.168.0.1',
...                 gocept.paypal.config_tests.BUYER_CC_NUMBER,
...                 gocept.paypal.config_tests.BUYER_CC_EXPDATE,
...                 '',
...                 'Sebastian',
...                 'Wehrmann',
...                 gocept.paypal.config_tests.BUYER_CC_TYPE,
...                 'Forsterstr. 3',
...                 'Halle',
...                 'Saxony-Anhalt',
...                 '06112',
...                 callback_url,
...                 callback_cancel_url,
...         )
>>> print status
''
