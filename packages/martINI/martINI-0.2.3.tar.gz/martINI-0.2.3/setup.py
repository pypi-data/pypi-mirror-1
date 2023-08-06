from setuptools import setup, find_packages
import sys, os

version = '0.2.3'

setup(name='martINI',
      version=version,
      description="edit .ini files from the command line",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='ini cli',
      author='Jeff Hammel',
      author_email='jhammel@openplans.org',
      url='http://openplans.org',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
         'WebOb',	
         'Paste',
         'PasteScript',
         'genshi'
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      ini-get = martini.main:get
      ini-set = martini.main:set
      ini-delete = martini.main:delete

      [paste.app_factory]
      main = martini.web:factory
      """,
      )
