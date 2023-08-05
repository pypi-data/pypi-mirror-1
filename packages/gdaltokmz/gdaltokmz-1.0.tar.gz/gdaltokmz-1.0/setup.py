#!/usr/bin/python

from distutils.core import setup
from sys import version

SHORTDESC="Allows conversion from a GDAL-supported raster geographic format to the KMZ format used by the free Google Earth client. See www.gdal.org and earth.google.com."

LONGDESC="""
gdaltokmz allows converting from any GDAL-supported raster geographic
format to the KMZ format used by the free Google Earth visualization
tool.

To perform the conversion, call::

	gdaltokmz.convert_gdal_to_kmz(gdalfile,kmzfile)

Where gdalfile is the path to the input file, and kmzfile is the name
of the file to be output.

This module requires that the gdal and osr python modules be installed.
More information on these can be found at http://www.gdal.org.

This module requires the presence of ImageMagick's "convert" tool. Its
location is hardcoded into the library as /usr/lib/convert; make sure
to change it if your copy lives somewhere else (e.g., on a Windows
machine). See http://www.imagemagick.org.

To view the output files requires Google's free Google Earth program.
See http://earth.google.com."""

AUTHOR="Imran Haque"
AUTHOR_EMAIL="ihaque@cs.stanford.edu"
URL="http://gecensus.stanford.edu/gcensus-gt"

CLASSIFIERS = [	'Operating System :: OS Independent',
		'License :: OSI Approved :: GNU General Public License (GPL)',
		'Topic :: Scientific/Engineering :: GIS',
		'Topic :: Utilities',
		'Topic :: Multimedia :: Graphics :: Graphics Conversion']


if version < '2.2.3':
	from distutils.dist import DistributionMetadata
	DistributionMetadata.classifiers = None
	DistributionMetadata.download_url = None

setup(	name='gdaltokmz',
	version='1.0',
	py_modules=['gdaltokmz'],
	license = 'GPL',
	description=SHORTDESC,
	long_description=LONGDESC,
	author=AUTHOR,
	author_email=AUTHOR_EMAIL,
	classifiers = CLASSIFIERS,
	url=URL)
