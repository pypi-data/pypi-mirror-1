from setuptools import setup, find_packages
import sys, os

version = '1.0rc1'

def read(*pathnames):
    return open(os.path.join(os.path.dirname(__file__), *pathnames)).read()

setup(name='vice.plone.outbound',
      version=version,
      description="Plone package for outbound syndication.",
      long_description='\n'.join([
          read('docs', 'README.txt'),
          read('docs', 'INSTALL.txt'),
          read('docs', 'HISTORY.txt'),
          ]),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='syndication atom rdf rss zope feeds plone',
      author='Derek Richardson',
      author_email='syndication@derekrichardson.net',
      url='http://www.openplans.org/projects/vice/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['vice','vice.plone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'setuptools',
          'vice.zope2.outbound',
          'rwproperty',
          'plone.browserlayer',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
