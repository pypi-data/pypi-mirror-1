from setuptools import setup, find_packages
import sys, os

version = '1.0'
longdesc = """\
An Archetypes Schema is looked up several times each request an Archetypes is 
accessed, like 60 times or more (depends on the number of fields).

This package patches the ``Schema`` method on ``BaseObject``. The Schema is 
now calculated only once and then cached in RamCache. The cache-key takes care 
about class-name, portal_type and interfaces provided by the Archetypes object.
any suggestions what else needed are welcome. It works fine with 
``archetypes.schemaextender`` and speeds it up. 

The package does not contain tests. To verify its working just run the 
Archetypes tests.

To enable the package you need to import the module somewhere in your code OR 
you need to include the configure.zcml i.e. in your buildout.

The module expects an eggified version of Archetypes like its shipped with Plone 
3.2 - or some fake-egg for ``Products.Archetypes``.
"""

setup(name='archetypes.schematuning',
      version=version,
      description="Archetypes Schema caching - a tune up patch.",
      long_description=longdesc,
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Framework :: Plone',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.4',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
          'Topic :: Software Development :: Libraries :: Application Frameworks',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Jens Klein',
      author_email='jens@bluedynamics.com',
      url='http://bluedynamics.com',
      license='GPL',
      packages=find_packages('src'),
      package_dir = {'' : 'src'},
      namespace_packages=['archetypes',],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'plone.memoize',
          'Products.Archetypes',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
