# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: setup.py 5737 2008-05-17 08:20:00Z sweh $

import sys
import os.path

from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name='gocept.paypal',
    version='0.1.9',
    description="Paypal Utility providing the paypal API",
    long_description = (read('README.txt')
                         + '\n\n' +
                         read('src', 'gocept', 'paypal',
                             'paypal.txt')
                         + '\n\n' +
                         read('CHANGES.txt')
    ),
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP'],
    url='http://pypi.python.org/pypi/gocept.paypal/',
    keywords='zope3 gocept paypal',
    author='Sebastian Wehrmann, Daniel Havlik',
    author_email='sw@gocept.com',
    license='ZPL 2.1',
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe=False,
    install_requires=[
        'zc.testbrowser',
        'zope.interface',
        'zope.component'
       ],
    )
