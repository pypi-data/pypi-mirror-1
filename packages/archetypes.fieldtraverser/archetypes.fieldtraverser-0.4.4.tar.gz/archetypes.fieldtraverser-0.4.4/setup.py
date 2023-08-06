# -*- coding: utf-8 -*-
#
# Copyright 2008, Blue Dynamics Alliance, Austria - http://bluedynamics.com
#
# GNU General Public Licence Version 2 or later

__author__ = """Jens Klein, Johannes Raggam"""
__docformat__ = 'plaintext'

from setuptools import setup, find_packages
import os

version = '0.4.4'
shortdesc = "Archetypes fieldtraverser"
longdesc = open(os.path.join(os.path.dirname(__file__),
                             'src', 'archetypes',
                             'fieldtraverser', 'README.txt')).read()

setup(name='archetypes.fieldtraverser',
    version=version,
    description=shortdesc,
    long_description=longdesc,
    classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Web Environment',
            'Framework :: Zope2',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    keywords='archetypes fieldtraverser',
    author='Jens Klein, Johannes Raggam',
    author_email='dev@bluedynamics.com',
    url='http://svn.plone.org/svn/archetypes/archetypes.fieldtraverser',
    license='GPL',
    packages=find_packages('src'),
    package_dir = {'' : 'src'},
    namespace_packages=['archetypes'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        # -*- Extra requirements: -*
        'Products.Archetypes',
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,
)