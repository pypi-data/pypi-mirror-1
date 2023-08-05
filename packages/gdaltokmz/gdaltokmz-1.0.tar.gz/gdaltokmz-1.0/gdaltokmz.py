#!/usr/bin/python

import gdal
import osr
import os
import warnings
import zipfile
from gdalconst import *

convert_path = '/usr/bin/convert'

def open_gdal(filename):
	"""Opens a GDAL dataset from the given file or fails out"""
	dataset = gdal.Open(filename,GA_ReadOnly)
	if dataset is None:
		print "Error opening dataset!"
	return dataset
#end open_gdal

    

def convert_to_png(dataset,outfile):
	"""
	Converts the given dataset to a PNG raster image through a GIF
	intermediate with ImageMagick.
	The PNG output direct form GDAL *cannot* be read using Google Earth, so
	we add indirection through GIF.
	"""
	
	# tmpnam is supposedly a sec hazard, but the GDAL library wants a real filename...
	warnings.filterwarnings("ignore","tmpnam is a potential security risk")
	outname = os.tmpnam()
	warnings.resetwarnings()
	
	gdal.GetDriverByName("GIF").CreateCopy(outname,dataset,0)

	os.spawnl(os.P_WAIT,convert_path,convert_path,outname,'png:%s' % outfile)
	os.unlink(outname)
	return
#end convert_to_png

def bounding_box_wgs84(dataset):
	"""Returns the bounding box (N,S,E,W) for the dataset, in WGS84 cords"""

	srs_dataset = osr.SpatialReference()
	srs_dataset.ImportFromWkt(dataset.GetProjection())
	srs_ge = osr.SpatialReference()
	srs_ge.SetWellKnownGeogCS("WGS84")


	xform = osr.CoordinateTransformation(srs_dataset,srs_ge)

	xsize = dataset.RasterXSize
	ysize = dataset.RasterYSize
	geotransform = dataset.GetGeoTransform()
	
	topleft = xform.TransformPoint(geotransform[0],geotransform[3])
	xExtent = xsize * geotransform[1]
	yExtent = ysize * geotransform[5]
	
	# Origin is specified as top-left corner of image
	# Want to return in order NSEW
	return (geotransform[3],geotransform[3]+yExtent,geotransform[0]+xExtent,geotransform[0])
# end bounding_box_wgs84

def kml_string(bbox,pngname,drivername):
	"""Returns a string containing a KML file for the ground overlay representing the file"""
	kml = '''<?xml version="1.0" encoding="utf-8"?>
	<kml xmlns="http://earth.google.com/kml/2.1">
	<Document>
	<name>gCensus-converted %s map</name>
	<GroundOverlay>
	<name>gCensus %s Conversion</name>
	<Icon>
		<href>%s</href>
	</Icon>
	<LatLonBox>
		<north>%f</north>
		<south>%f</south>
		<east>%f</east>
		<west>%f</west>
	</LatLonBox>
	</GroundOverlay>
	</Document>
	</kml>''' % ((drivername,drivername,pngname)+bbox)
	return kml
# end kml_string

def convert_gdal_to_kmz(gdalfile,kmzfile):
	"""
	Convert a GDAL-readable raster file to Google Earth KMZ format.
	
	Arguments:
	gdalfile: path to a GDAL-readable raster file
	kmzfile:  name of the KMZ file to be written
	"""
	
	ds = open_gdal(gdalfile)
	#print "Driver: ",ds.GetDriver().ShortName,'/',ds.GetDriver().LongName
	
	warnings.filterwarnings("ignore","tmpnam is a potential security risk")
	pngtmp = os.tmpnam()
	warnings.resetwarnings()
	
	convert_to_png(ds,pngtmp)
	bbox = bounding_box_wgs84(ds)

	kmz = zipfile.ZipFile(kmzfile,"w")
	kml_png_path = os.path.join('files',os.path.basename(pngtmp))
	kmz.writestr('yourmap.kml',kml_string(bbox,kml_png_path,ds.GetDriver().LongName))
	kmz.write(pngtmp,kml_png_path)
	kmz.close()
	
	os.unlink(pngtmp)
# end convert_gdal_to_ge
