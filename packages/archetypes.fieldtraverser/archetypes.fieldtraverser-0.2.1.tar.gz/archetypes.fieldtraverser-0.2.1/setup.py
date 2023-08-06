# -*- coding: utf-8 -*-
#
# Copyright 2006-2008, BlueDynamics Alliance, Austria
# www.bluedynamics.com
#
# GNU General Public Licence Version 2 or later - see LICENCE.GPL

"""
setup.py bdist_egg
"""

from setuptools import setup, find_packages
import os

version = '0.2.1'
shortdesc = "Archetypes fieldtraverser"
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()

setup(
    name='archetypes.fieldtraverser',
    version=version,
    description=shortdesc,
    long_description=longdesc,
    classifiers=[
            'Development Status :: 4 - Beta',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Operating System :: OS Independent',
            'Programming Language :: Python',          
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
    ],
    entry_points="""
      # -*- Entry points: -*-
      """,
)