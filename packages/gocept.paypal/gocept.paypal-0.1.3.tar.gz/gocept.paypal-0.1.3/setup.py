from setuptools import setup, find_packages
import sys, os

version = '0.1.3'

setup(name='gocept.paypal',
      version=version,
      description="Paypal Utility providing the paypal API",
      long_description="",
      classifiers=[], 
      keywords='',
      author='Sebastian Wehrmann, Daniel Havlik',
      author_email='sw@gocept.com',
      url='gocept.com',
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
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
