from setuptools import setup, find_packages
import sys, os

version = '1.0.0'

longdescription = open(os.path.join(os.path.dirname(__file__), 
                                    'README.txt')).read()

setup(name='Products.basesyndication',
      version=version,
      description="Basic Syndication interfaces and templates",
      long_description=longdescription,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone syndication atom rss',
      author='Tim Hicks',
      author_email='tim@sitefusion.co.uk',
      url='http://dev.plone.org/collective/browser/Products.basesyndication',
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
