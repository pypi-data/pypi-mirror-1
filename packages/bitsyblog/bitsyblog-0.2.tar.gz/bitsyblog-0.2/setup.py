from setuptools import setup, find_packages
import sys, os

version = '0.2'

setup(name='bitsyblog',
      version=version,
      description="a tiny tiny blog",
      long_description="""\
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
          'dateutil'
      ],
      entry_points="""
      # -*- Entry points: -*-
      [paste.app_factory]
      main = bitsyblog.wsgiapp:make_app
      """,
      )
