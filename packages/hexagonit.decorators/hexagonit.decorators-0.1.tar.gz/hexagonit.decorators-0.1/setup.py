from setuptools import setup, find_packages
import sys, os

version = '0.1'
name = 'hexagonit.decorators'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(name=name,
      version=version,
      description="Collection of useful decorators for Zope development",
      long_description= (
        read('README.txt')
        + '\n' +
        read('CHANGES.txt')
        + '\n' +
        'Detailed Documentation\n'
        '**********************\n'
        + '\n' +
        read('src','hexagonit','decorators','README.txt')
        + '\n' +
        'Download\n'
        '***********************\n'
        ),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Framework :: Zope2',
        'Framework :: Zope3',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
      keywords='',
      author='Kai Lautaportti',
      author_email='kai.lautaportti@hexagonit.fi',
      url='http://pypi.python.org/pypi/%s' % name,
      license='GPL',
      packages=find_packages('src'),
      package_dir={'':'src'},
      namespace_packages=['hexagonit'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
          'simplejson'
      ],
      tests_require = ['zope.testing'],
      test_suite = '%s.tests.test_suite' % name,
      )
