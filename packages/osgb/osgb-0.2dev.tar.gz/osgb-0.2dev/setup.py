#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A setup script using setuptools.

If run like this::

	python setup.py install

it will install itself into the appropriate python's site packages. Although
not everyone will have setuptools, ``ez_setup.py`` is included as a bootstrap.
Those who do have setuptools, but don't have a constant internet connection
can always download a package or egg. Those who have neither are kinda stuck.

"""

### IMPORTS ###

# ensure setuptools is available
#from ez_setup import use_setuptools
#use_setuptools()
from setuptools import setup, find_packages
import sys, os


### CONSTANTS & DEFINES ###

from osgb import __version__


### SETUP ###

setup (
	name='osgb',
	version=__version__,
	description="Inter-conversion of OSGB references and lon-lats",
	long_description="""\
	Many geospatial locations within the UK are given with the (accurate but peculiar to the UK) Ordnance Survey system. This module presents functions for converting between these and the most widely spread longitude-latitude system.""",
	classifiers=[
		'Development Status :: 4 - Beta',
		'Intended Audience :: Science/Research',
		'License :: OSI Approved :: BSD License',
		'Topic :: Scientific/Engineering :: GIS',
	],
	keywords='geospatial OSGB UK',
	author='Paul-Michael Agapow',
	author_email='agapow@bbsrc.ac.uk',
	url='http://www.agapow.net/software/osgb',
	license='BSD',
	packages=find_packages(exclude=['ez_setup', 'examples', 'tests', 'test']),
	test_suite = 'nose.collector',
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		# -*- Extra requirements: -*-
	],
	entry_points="""
		# -*- Entry points: -*-
	""",
)


### END ###
