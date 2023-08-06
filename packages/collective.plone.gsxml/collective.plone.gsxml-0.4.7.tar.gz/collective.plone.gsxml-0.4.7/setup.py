from setuptools import setup, find_packages
import sys, os

version = '0.4.7'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    'Change history\n'
    '==============\n'
    + '\n' +
    read('CHANGES.txt')
    + '\n' +
    'Detailed Documentation\n'
    '======================\n'
    + '\n' +
    read('src', 'collective', 'plone', 'gsxml', 'README.rst')
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n' +
    'Download\n'
    '========\n'
    )


setup(name='collective.plone.gsxml',
      version=version,
      description="A package for importing and exporting content from Plone",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Plone import export XML',
      author='Stefan Eletzhofer, Ramon Bartl',
      author_email='stefan.eletzhofer@inquant.de',
      url='https://svn.plone.org/svn/collective/gsxml/releases/0.4.7',
      license='GPL',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['collective', 'collective.plone'],
      include_package_data=True,
      zip_safe=False,
      test_suite = 'collective.plone.gsxml.tests',
      extras_require = dict(
        test = [
            'zope.app.testing',
            'zope.interface',
            ],
        ),
      install_requires=[
        'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
