from setuptools import setup, find_packages
import sys, os

version = "0.2"

setup(name='lxmlmiddleware',
      version=version,
      description="stack of middleware to deal with a response as a LXML etree",
      long_description="""
""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      author='Jeff Hammel',
      author_email='k0scist@gmail.com',
      url='http://k0s.org/hg/lxmlmiddleware',
      license="",
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
         'WebOb',	
         'Paste',
         'PasteScript',
         'lxml',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.app_factory]
      example = lxmlmiddleware.example:factory
      """,
      )
      
