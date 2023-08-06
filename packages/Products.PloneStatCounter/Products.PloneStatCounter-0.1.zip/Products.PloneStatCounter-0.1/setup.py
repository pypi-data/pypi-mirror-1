from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='Products.PloneStatCounter',
      version=version,
      description="A package to ease use of StatCounter in Plone.",
      long_description="""\
This package makes it easy to include a StatCounter page counter in a Plone \
site. It provides ttw configuration on a per-Plone-instance basis.
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Tim Hicks',
      author_email='tim@sitefusion.co.uk',
      url='http://svn.plone.org/svn/collective/Products.PloneStatCounter',
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
