from setuptools import setup, find_packages
import sys, os

# get the description from the README
try:
    filename = os.path.join(os.path.dirname(__file__), 'README.txt')
    description = file(filename).read()
except:
    description = ''

version = "0.1.1"

setup(name='redirector',
      version=version,
      description="WSGI middleware/app for managing redirects",
      long_description=description,
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      author='Jeff Hammel',
      author_email='k0scist@gmail.com',
      url='http://k0s.org/hg/redirector',
      license="GPL",
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
         'WebOb',	
         'Paste',
         'PasteScript',
         'genshi',
         'python-dateutil',
         
      ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.app_factory]
      main = redirector.factory:factory

      [redirector.redirectors]
      test-redirector = redirector.redirectors:TestRedirector
      ini-redirector = redirector.redirectors:IniRedirector
      """,
      )
      
