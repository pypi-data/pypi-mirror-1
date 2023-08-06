from setuptools import setup, find_packages
import os

version = open(os.path.join("getpaid", "SalesforceOrderRecorder", "version.txt")).read().strip()

setup(name='getpaid.SalesforceOrderRecorder',
      version=version,
      description="GetPaid plugin allowing for storage or orders in Salesforce.com",
      long_description=open(os.path.join("getpaid", "SalesforceOrderRecorder", "README.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Zope2",
        "Framework :: Plone",
        ],
      keywords='Zope CMF Plone Salesforce.com CRM integration',
      author='Rob LaRubbio',
      author_email='rob@onenw.org',
      url='http://code.google.com/p/getpaid',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['getpaid'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'beatbox>=0.9,<=1.0dev',
          'Products.salesforcebaseconnector'
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
