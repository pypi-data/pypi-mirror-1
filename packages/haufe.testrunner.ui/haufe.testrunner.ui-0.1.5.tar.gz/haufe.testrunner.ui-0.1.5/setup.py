import os
from setuptools import setup, find_packages

version = '0.1.5'
long_desc = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()
changes = open(os.path.join(os.path.dirname(__file__), 'CHANGES.txt')).read()
long_desc += '\nCHANGES\n=======\n\n' + changes

setup(name='haufe.testrunner.ui',
      version=version,
      description="Webfrontend for haufe.testrunner results",
      long_description=long_desc,
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[], 
      keywords="Grok testrunner Haufe webfrontend unittests Zope",
      author="Andreas Jung",
      author_email="andreas.jung@haufe.de",
      url="",
      license="ZPL",
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'grok',
                        'sqlalchemy',
                        'zope.sqlalchemy>=0.2.0',
                        'haufe.testrunner>=0.6.1',
                        # Add extra requirements here
                        ],
      entry_points="""
      # Add entry points here
      """,
      )
