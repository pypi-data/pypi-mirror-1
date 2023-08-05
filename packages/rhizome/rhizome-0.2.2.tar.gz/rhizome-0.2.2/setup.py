from setuptools import setup, find_packages
import sys, os

version = '0.2.2'

setup(name='rhizome',
      version=version,
      description="'generalized rdf store for zope2 and zope3'",
      long_description=\
      """
      Rhizome is a light wrapper around the primary graphs of the
      rdflib 2.3.3 using the ZODB and zope3's component libs.

      includes a `five` implementation for using in zope2
      """,
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='zope2 zope3 rdf annotations yucca',
      author='whit',
      author_email='whit@openplans.org',
      url='http://openplans.org/projects/yucca',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['rhizome'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['rdflib==2.3.1events',
                        'five.intid>=0.1.3',
                        ],
      dependency_links=[
                        'http://www.openplans.org/projects/yucca/install-tagger',
                        'http://svn.rdflib.net/branches/michel-events#egg=rdflib-2.3.1events',       
                        ],
      
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
