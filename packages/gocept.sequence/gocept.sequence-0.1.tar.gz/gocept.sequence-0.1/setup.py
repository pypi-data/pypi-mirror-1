from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='gocept.sequence',
      version=version,
      description="Generates a sequence",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Daniel Havlik',
      author_email='dh@gocept.com',
      url='http://www.gocept.com',
      license='ZPL 2.1',
      packages = find_packages('src'),
      package_dir = {'': 'src'},
      include_package_data = True,
      zip_safe = False,
      install_requires=[
        'setuptools'
          ],
      extras_require = dict(zope3=[
         'Persistence',
          'zope.component',
         'zope.interface',
         'zope.annotation'
          ]),
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
