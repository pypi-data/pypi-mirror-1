from setuptools import setup, find_packages
import os

version = '0.1-step02'

setup(name='Products.Andreas09Theme',
      version=version,
      description="An example theme for Plone 3.0",
      long_description=open("README.txt").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='web zope plone theme example tutorial how-to',
      author='David Convent',
      author_email='product-developers@lists.plone.org',
      url='http://pypi.python.org/pypi/Products.Andreas09Theme',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
