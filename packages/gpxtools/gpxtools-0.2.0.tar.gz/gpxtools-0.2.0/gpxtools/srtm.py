# -*- coding: utf-8 -*-
"""
Provides an interface to SRTM elevation data stored in GeoTIFF Files.
"""
import sys, random, re, os.path, urllib2, zipfile
from math import floor, ceil
from cStringIO import StringIO

from osgeo import gdal, gdalnumeric

import logging as log
log.basicConfig(level=log.INFO, format='%(levelname)s %(message)s')


def bilinear_interpolation(tl, tr, bl, br, a, b):
    """
    Based on equation from:
    http://en.wikipedia.org/wiki/Bilinear_interpolation
    
    :Parameters:
        tl : int
            top-left
        tr : int
            top-right
        bl : int
            buttom-left
        br : int
            bottom-right
        a : float
            x distance to top-left
        b : float
            y distance to top-right

    :Returns: (float)
        interpolated value
    """
    b1 = tl
    b2 = bl - tl
    b3 = tr - tl
    b4 = tl - bl - tr + br

    return b1 + b2 * a + b3 * b + b4 * a * b


class SrtmTiff(object):
    """
    Provides an interface to SRTM elevation data stored in GeoTIFF file.
    
    Based on code from `eleserver` code by grahamjones139.
    http://code.google.com/p/eleserver/
    """
    tile = {}
    
    def __init__(self, filename):
        """
        Reads the GeoTIFF files into memory ready for processing.
        """
        self.tile = self.load_tile(filename)
    
    def load_tile(self, filename):
        """
        Loads a GeoTIFF tile from disk and returns a dictionary containing
        the file data, plus metadata about the tile.

        The dictionary returned by this function contains the following data:
            xsize - the width of the tile in pixels.
            ysize - the height of the tile in pixels.
            lat_origin - the latitude of the top left pixel in the tile.
            lon_origin - the longitude of the top left pixel in the tile.
            lat_pixel - the height of one pixel in degrees latitude.
            lon_pixel - the width of one pixel in degrees longitude.
            N, S, E, W - the bounding box for this tile in degrees.
            data - a two dimensional array containing the tile data.

        """
        dataset = gdal.Open(filename)
        geotransform = dataset.GetGeoTransform()
        xsize = dataset.RasterXSize
        ysize = dataset.RasterYSize
        lon_origin = geotransform[0]
        lat_origin = geotransform[3]
        lon_pixel = geotransform[1]
        lat_pixel = geotransform[5]
        
        retdict = {
            'xsize': xsize,
            'ysize': ysize,
            'lat_origin': lat_origin,
            'lon_origin': lon_origin,
            'lon_pixel': lon_pixel,
            'lat_pixel': lat_pixel,
            'N': lat_origin,
            'S': lat_origin + lat_pixel*ysize,
            'E': lon_origin + lon_pixel*xsize,
            'W': lon_origin,
            'dataset': dataset,
            }
        
        return retdict  

    def pos_from_lat_lon(self, lat, lon):
        """
        Converts coordinates (lat,lon) into the appropriate (row,column)
        position in the GeoTIFF tile data stored in td.
        """
        td = self.tile
        N = td['N']
        S = td['S']
        E = td['E']
        W = td['W']
        lat_pixel = td['lat_pixel']
        lon_pixel = td['lon_pixel']
        xsize = td['xsize']
        ysize = td['ysize']
        
        rowno_f = (lat-N)/lat_pixel
        colno_f = (lon-W)/lon_pixel
        rowno = int(floor(rowno_f))
        colno = int(floor(colno_f))

        # Error checking to correct any rounding errors.
        if (rowno<0):
            rowno = 0
        if (rowno>(xsize-1)):
            rowno = xsize-1
        if (colno<0):
            colno = 0
        if (colno>(ysize-1)):
            colno = xsize-1
            
        return (rowno, colno, rowno_f, colno_f)
    
    def get_elevation(self, lat, lon):
        """
        Returns the elevation in metres of point (lat, lon).
        
        Uses bilinar interpolation to interpolate the SRTM data to the
        required point.
        """
        row, col, row_f, col_f = self.pos_from_lat_lon(lat, lon)

        # NOTE - THIS IS A FIDDLE TO STOP ERRORS AT THE EDGE OF
        # TILES - IT IS NO CORRECT - WE SHOULD GET TWO POINTS 
        # FROM THE NEXT TILE.
        if row==5999: row=5998
        if col==5999: col=5998

        htarr = gdalnumeric.DatasetReadAsArray(self.tile['dataset'], col, row, 2, 2)
        height = bilinear_interpolation(htarr[0][0], htarr[0][1], htarr[1][0], htarr[1][1],
                                       row_f-row, col_f-col)

        return height


class SrtmLayer(object):
    """
    Provides an interface to SRTM elevation data stored in GeoTIFF files.
    
    Files are automaticly downloaded from mirror server and cached in
    `~/.gpxtools` directory.
    
    Sample usage:
    
        >>> lat = 52.25
        >>> lon = 16.75
        >>> srtm = SrtmLayer()
        >>> ele = srtm.get_elevation(lat, lon)
        >>> round(ele, 4)
        63.9979
        
    """
    _cache = {}
    
    def _download_srtm_tiff(self, srtm_filename):
        """
        Download and unzip GeoTIFF file.
        """
        log.info('Downloading SRTM data file, it may take some time ...')
        url = 'http://hypersphere.telascience.org/elevation/cgiar_srtm_v4/tiff/zip/%s.ZIP' % srtm_filename[:-4]
        zobj = StringIO()
        zobj.write(urllib2.urlopen(url).read())
        z = zipfile.ZipFile(zobj)

        gpxtools_dir = os.path.expanduser('~/.gpxtools')
        if not os.path.isdir(gpxtools_dir):
            os.path.mkdir(gpxtools_dir)
        
        srtm_path = os.path.join(gpxtools_dir, srtm_filename)
        out_file = open(srtm_path, 'w')
        out_file.write(z.read(srtm_filename))
        
        z.close()
        out_file.close()
        
    def get_srtm_filename(self, lat, lon):
        """
        Filename of GeoTIFF file containing data with given coordinates.
        """
        colmin = floor((6000 * (180 + lon)) / 5)
        rowmin = floor((6000 * (60 - lat)) / 5)
    
        ilon = ceil(colmin / 6000.0)
        ilat = ceil(rowmin / 6000.0)
        
        return 'srtm_%02d_%02d.TIF' % (ilon, ilat)
    
    def get_elevation(self, lat, lon):
        """
        Returns the elevation in metres of point (lat, lon).
        """
        srtm_filename = self.get_srtm_filename(lat, lon)
        if srtm_filename not in self._cache:
            srtm_path = os.path.join(os.path.expanduser('~/.gpxtools'), srtm_filename)
            if not os.path.isfile(srtm_path):
                self._download_srtm_tiff(srtm_filename)
                            
            self._cache[srtm_filename] = SrtmTiff(srtm_path)
        
        srtm = self._cache[srtm_filename]
        return srtm.get_elevation(lat, lon)
