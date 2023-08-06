#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Various constants for the coordinate conversion.

"""

__docformat__ = 'restructuredtext en'


### IMPORTS ###

from math import radians

__all__ = [
	'ORIGIN_LAT',
	'ORIGIN_LON',
	'ORIGIN_NORTHING',
	'ORIGIN_EASTING',
	'OSGB36',
]


### CONSTANTS & DEFINES ###

# true origin of national grid
ORIGIN_LAT = radians (49) #* pi / 180
ORIGIN_LON = radians (-2) # * pi / 180
ORIGIN_NORTHING = -100000
ORIGIN_EASTING = 400000

# a collection of constants for conversion
# later we may use other projections
class OSGB36 (object):
	# Airy 1830 major & minor semi-axes
	a = 6377563.396 
	b = 6356256.910 
	# NatGrid scale factor on central meridian
	F0 = 0.9996012717
	# eccentricity squared                
	e2 = 1 - (b**2)/(a**2)                          
	n = (a-b)/(a+b)
	n2 = n**2
	n3 = n**3
	

### IMPLEMENTATION ###

### TEST & DEBUG ###

def _doctest ():
	import doctest
	doctest.testmod()
	
	
### MAIN ###

if __name__ == '__main__':
	_doctest()


### END ######################################################################
