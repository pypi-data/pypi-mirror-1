from setuptools import setup, find_packages
import os

version = '1.2'
shortdesc ="More Speed with cached Archetypes Schemas."
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read() + "\n" + \
           open(os.path.join(os.path.dirname(__file__), 'CONTRIBUTORS.txt')).read()

tests_require=[
            'archetypes.schemaextender',
            ]

setup(
    name='archetypes.schematuning',
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
    author='Jens Klein, Hedley Roos',
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
            'plone.memoize',
            'Products.Archetypes',
    ],
    tests_require=tests_require,
    extras_require=dict(tests=tests_require),
    entry_points="""
        [z3c.autoinclude.plugin]
        target = plone
        """,
      )
