from setuptools import setup, find_packages
import sys, os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.3'

setup(name='gocept.sequence',
      version=version,
      description="Generates a sequence",
      long_description = (read('src', 'gocept', 'sequence', 'README.txt')),
      classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP'],
      url='http://pypi.python.org/pypi/gocept.sequence/',
      keywords='sequence generator',
      author='Daniel Havlik, Sebastian Wehrmann',
      author_email='dh@gocept.com',
      license='ZPL 2.1',
      packages = find_packages('src'),
      package_dir = {'': 'src'},
      include_package_data = True,
      zip_safe = False,
      install_requires=[
        'setuptools'
          ],
      extras_require = dict(
          zope3=['Persistence',
                 'zope.component',
                 'zope.interface',
                 'zope.annotation'
                ],
          test=['zope.app.testing',
                'zope.app.zcmlfiles'],
      ),
     )
