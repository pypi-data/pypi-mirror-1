from setuptools import setup, find_packages
import sys, os

version = '1.0b1'

setup(name='collective.uuid',
      version=version,
      description="RFC 4122 universally unique identifier utility.",
      long_description="""\
This is a library for providing RFC 4122 uuid utilities in Zope 2 and Zope 3. 
It is modeled on zope.app.intid functionally, though much of the generic bits
are factored out into collective.baseid. Requires five.intid to run on Zope 2 
- this will not be installed by default, as it is a platform-specific 
dependency.
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='zope uuid',
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
          'collective.baseid',
          'uuid',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
