import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

name = 'zw.schema'
version = '0.3.0b1'

setup(name=name,

      # Fill in project info below
      version=version,
      description="Additional schema fields for Zope 3",
      long_description=(
        read('README.txt') +
        '\n\n' +
        read('src', 'zw', 'schema', 'color', 'README.txt') +
        '\n\n' +
        read('src', 'zw', 'schema', 'reference', 'README.txt') +
        '\n\n' +
        read('src', 'zw', 'schema', 'richtext', 'README.txt') +
        '\n\n' +
        read('CHANGES.txt')),
      keywords='zope3',
      author='Gregor Giesen',
      author_email='giesen@zaehlwerk.net',
      url='https://launchpad.net/'+name,
      license='GPLv3',
      # Get more from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Development Status :: 4 - Beta',
                   'Programming Language :: Python',
                   'Environment :: Web Environment',
                   'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
                   'Framework :: Zope3',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   ],

      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['zw'],
      include_package_data=True,
      zip_safe=False,
      extras_require = dict(
        test = ['zope.testing',
                ], ),
      install_requires = ['setuptools',
                          'zope.i18nmessageid',
                          'zope.interface',
                          'zope.schema',
                          'zope.app.intid',
                          ],
      )
