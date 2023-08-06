from setuptools import setup, find_packages
import sys, os

version = '1.1'
shortdesc ="More Speed with cached Archetypes Schemas."
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read() 

setup(name='archetypes.schematuning',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Framework :: Plone',
          'Framework :: Zope2',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
      ], # Get strings from 
      keywords='',
      author='Jens Klein, Hedyley Ross',
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
