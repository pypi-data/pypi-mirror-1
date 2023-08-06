from setuptools import setup, find_packages
import sys, os

try:
    description = file("README.txt").read()
except IOError:
    description = ''

version = '0.3.3'

setup(name='decoupage',
      version=version,
      description="Decoupage is the art of decorating an object by gluing colored paper cutouts onto it in combination with special paint effects ...",
      long_description=description,
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      author='Jeff Hammel',
      author_email='k0scist@gmail.com',
      url='http://explosivedecompression.net',
      license="",
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
         'WebOb',	
         'Paste',
         'PasteScript',
         'genshi',
         'martINI',
         ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      decoupage-templates = decoupage.templates:main
      decoupage-formatters = decoupage.formatters:main

      [paste.app_factory]
      main = decoupage.factory:factory

      [decoupage.formatters]
      ignore = decoupage.formatters:Ignore
      all = decoupage.formatters:All
      describe = decoupage.formatters:FilenameDescription
      title = decoupage.formatters:TitleDescription
      """,
      )
      
