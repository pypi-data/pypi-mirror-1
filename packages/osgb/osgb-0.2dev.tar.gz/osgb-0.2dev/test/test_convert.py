#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for 'osgb.convert', using nose.
"""

### IMPORTS ###

from osgb import convert


### CONSTANTS & DEFINES ###

### TESTS ###

def setup():
	pass

def teardown():
	pass
	
def test_zonecoord_to_eastnorth():
	# already done in doctest
	pass
	
def test_oszone_to_eastnorth():
	# already done in doctest
	pass
	
def test_osgb_to_lonlat():
	# already done in doctest
	pass

def  test_eastnorth_to_osgb():
	# already done in doctest
	pass

def test_lonlat_to_eastnorth():
	# already done in doctest
	pass

def test_lonlat_to_osgb():
	# already done in doctest
	pass
	
def test_roundtrip():
	"""
	Convert an OSGB ref to a lon-lat and back.
	
	Currently we're losing about a metre in resolution ("TM 11400 52500"
	becomes "TM 11399 52499").
	
	"""
	os_ref = "TM 11400 52500"
	lon, lat = convert.osgb_to_lonlat (os_ref)
	print lon, lat
	os_ref_out = convert.lonlat_to_osgb (lon, lat, digits=5)
	print os_ref_out
	assert (os_ref == os_ref_out)



### END ######################################################################
