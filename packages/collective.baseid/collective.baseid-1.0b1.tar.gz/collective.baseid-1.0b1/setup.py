from setuptools import setup, find_packages
import sys, os

version = '1.0b1'

setup(name='collective.baseid',
      version=version,
      description="Base interfaces and classes for id utilities.",
      long_description="""\
This is a framework library for creating id utilities in Zope 2 and Zope 3. It
is modeled on zope.app.intid, but requires specialization to provide any 
particular type of id, An example of its use is collective.uuid, which provides
RFC 4122 uuids.
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='zope',
      author='Derek Richardson',
      author_email='syndication@derekrichardson.net',
      url='http://www.openplans.org/projects/vice/',
      license='ZPL,GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
