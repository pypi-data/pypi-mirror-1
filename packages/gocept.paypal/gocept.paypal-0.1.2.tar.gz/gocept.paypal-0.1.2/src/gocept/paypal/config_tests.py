# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: config_tests.py.example 5417 2007-11-22 10:01:48Z nilo $
"""Paypal test values for gocept.paypal package"""

USERNAME = 'bigbro_1195810768_biz_api1.gocept.com' # Edit this to your API user name
PASSWORD = 'D8ECYMLP7F5BJX6U' # Edit this to your API password
SIGNATURE = 'AZvJHrr7pu4zP4frBwHelJXJuHHaA7bp9a-x.MG2LyzgoyhU198mNrq1' # Edit this to your API signature
#USERNAME = 'sw-sel_1195726631_biz_api1.gocept.com' # Edit this to your API user name
#PASSWORD = 'GB5A4D94K84QPTQM' # Edit this to your API password
#SIGNATURE = 'ALUrIuLm3aacefUrly2K-pTVhgRoAfcebF1DJAKQnM58-NvymcRIiiaT' # Edit this to your API signature

VERSION = '3.0'
# Sandbox URL, not production
API_ENDPOINT = 'https://api-3t.sandbox.paypal.com/nvp'
PAYPAL_URL = 'https://www.sandbox.paypal.com/webscr'\
                '&cmd=_express-checkout&token='
CALLBACK_URL = 'http://paypaltest.gocept.com/~pmp/paypaltest/'
CALLBACK_CANCEL_URL = 'http://paypaltest.gocept.com/~pmp/paypaltest/'

# Edit this to your buyers email address and password
BUYER_EMAIL = 'testbu_1195748419_per@gocept.com'
BUYER_PASSWORD = '12345678'
BUYER_CC_NUMBER = '4594998465147592' # max 19 digits
BUYER_CC_TYPE = 'Visa' # Type of your credit card
BUYER_CC_EXPDATE = '022017' # expire date MMYY

# Edit this to your developer email address and passwords
DEVELOPER_LOGIN = 'sw@gocept.com'
DEVELOPER_PASSWORD = 'krabappel'
