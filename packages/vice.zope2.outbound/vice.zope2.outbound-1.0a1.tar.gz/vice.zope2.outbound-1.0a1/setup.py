from setuptools import setup, find_packages
import sys, os

version = '1.0a1'

setup(name='vice.zope2.outbound',
      version=version,
      description="Zope2 library for outbound syndication.",
      long_description="""\
vice.zope2.outbound provides Zope 2 with the ability to syndicate web feeds 
(rss, atom, etc). It is configurable by users and extensible by developers.

Zope requirement: version 2.10
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='syndication atom rdf rss zope feeds',
      author='Derek Richardson',
      author_email='syndication@derekrichardson.net',
      url='http://www.openplans.org/projects/vice/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['vice', 'vice.zope2'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'setuptools',
          'vice.outbound',
          'five.intid',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
