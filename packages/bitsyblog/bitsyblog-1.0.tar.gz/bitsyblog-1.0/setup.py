from setuptools import setup, find_packages
import sys, os

version = '1.0'

try:
    description = file('README.txt').read()
except IOError:
    description = """
Meet bitsyblog.  Posting is done with a POST request, so while you can use
a web form to do this, its just as easy to use curl, urllib, or anything else 
to post.
"""

setup(name='bitsyblog',
      version=version,
      description="a tiny tiny blog",
      long_description=description,
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='blog',
      author='Jeff Hammel',
      author_email='jhammel@openplans.org',
      url='http://bitsyblog.biz',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'WebOb',
          'Paste',
          'PasteScript',
          'dateutil',
          'markup',
          'skimpygimpy',
          'lxml',
          'PyRSS2Gen'
      ],
      dependency_links=[ 
        'https://svn.openplans.org/svn/standalone/markup#egg=markup',
        'http://svn.pythonpaste.org/Paste/trunk#egg=Paste',
        'http://downloads.sourceforge.net/skimpygimpy/skimpyGimpy_1_3.zip#egg=skimpygimpy',
        'http://www.dalkescientific.com/Python/PyRSS2Gen-1.0.0.tar.gz#egg=PyRSS2Gen'
        ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.app_factory]
      main = bitsyblog.factory:factory
      """,
      )
