#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Functions for interpreting and converting Ordnance Survey references.

Many geospatial locations within the UK are given with the Ordnance Survey
system. While common and highly accurate, this coordinate system is peculiar
to the UK and incompatiable with many modern cartography tools. This module presents functions for converting between these and the most widely spread longitude-latitude system.


Usage
~~~~~

`osgb` provides two primary functions, `osgb_to_lonlat` and `lonlat_to_osgb`, which are imported into the top of this package. Some of the intermediate conversions are provided for those who may find them
useful (e.g. for working in eastings-northings).


Caveats and bugs
~~~~~~~~~~~~~~~~

By convention, longitude and latitude are referred and used in that order.

Note that the lon-lats are returned are OSGB36 (not the more modern WGS84),
as that is the system OSGB is based upon. The difference should be minimal
(i.e. less than 100 metres). For example, the OS grid reference ``TM114 525``
(just outside Ipswich) should convert to the lon-lat ``1.088975 52.129892`` in 
OSGB36, which is ``1.087203 52.130350`` in WGS84.

Currently, "round-tripping" an OS reference to a lon-lat and then converting
it back results in the loss of about a metre of accuracy. This is regarded
as acceptable, but does result in two of the built-in tests failing due to
a single meter discrepancy.


References
~~~~~~~~~~

* The Ordnance Survey provides `a guide to coordinate systems
  <http:#www.ordnancesurvey.co.uk/oswebsite/gps/information/coordinatesystemsinfo/guidecontents/index.html>`__,
  the `equations for conversion
  <http:#www.ordnancesurvey.co.uk/oswebsite/gps/information/coordinatesystemsinfo/guidecontents/guidec.html>`__
  and the `required constants
  <http:#www.ordnancesurvey.co.uk/oswebsite/gps/information/coordinatesystemsinfo/guidecontents/guidea.html>`__.

* A nice explanation of the OSGB system can be found `here <http://vancouver-webpages.com/peter/osgbfaq.txt>`__

* J Stott provides a `PHP library <http:#www.jstott.me.uk>`__ as well as
  Javascript and Java implementations.  Chris Veness' `Javascript
  implementation <http:#www.movable-type.co.uk/scripts/latlong-gridref.html>`__
  was a useful reference in the conversion, as was A. Rutherfords `Geoposition <http://ccgi.arutherford.plus.com/website/GeoPosition/>`__.  The `Perl module
  Geo::Coordinates::OSGB <http://search.cpan.org/~toby/Geo-Coordinates-OSGB-2.01/lib/Geo/Coordinates/OSGB.pm>`__ provides similar services.

* `Nearby.org.uk <http:#nearby.org.uk>`__ provides conversion between many
  geospatial formats including OS.

"""
# TODO: convert x,y format coordinates?
# TODO: better naming?
# TODO: is there a formal name for the large and small squares?
# TODO: is there a way to directly convert to WGS84?
# TODO: a class (OSRef?) to allow OS grid geometry.

__docformat__ = 'restructuredtext en'


### IMPORTS ###

from convert import osgb_to_lonlat
from convert import lonlat_to_osgb


### CONSTANTS & DEFINES ###

__version__ = '0.2'

	

### IMPLEMENTATION ###

### TEST & DEBUG ###

def _doctest ():
	import doctest
	doctest.testmod()
	
	
### MAIN ###

if __name__ == '__main__':
	_doctest()


### END ######################################################################
