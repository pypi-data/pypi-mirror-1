from setuptools import setup, find_packages
import sys, os

version = '0.4'

setup(name='bitsyblog',
      version=version,
      description="a tiny tiny blog",
      long_description="""
      Meet bitsyblog.  Posting is done with a POST request, so while you can use
a web form to do this, its just as easy to use curl, urllib, or anything else 
to post.

""",
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
      ],
      dependency_links=[ 'https://svn.openplans.org/svn/standalone/markup#egg=markup', ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.app_factory]
      main = bitsyblog.wsgiapp:make_app
      """,
      )
