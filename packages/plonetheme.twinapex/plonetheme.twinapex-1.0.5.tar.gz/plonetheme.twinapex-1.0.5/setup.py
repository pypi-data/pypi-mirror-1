__author__ = "Twinapex Research <research@twinapex.com>"
__author_url__ = "http://www.twinapex.com"
__copyright__ = "2009 Twinapex Research"
__license__ = "GPL"
__docformat__ = "epytext"

from setuptools import setup, find_packages

version = '1.0.5'

setup(name='plonetheme.twinapex',
      version=version,
      description="Twinapex Theme is a theming product for Plone to give your site a professional corporate look",
      long_description=open("README.txt").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='twinapex web zope plone theme skin corporate',
      author='Mikko Ohtamaa',
      author_email='research@twinapex.com',
      url='http://www.twinapex.com',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plonetheme'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'plone.browserlayer',
          'archetypes.schemaextender',
          'webcouturier.dropdownmenu==1.1.5',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
