# -*- coding: utf-8 -*-
"""
Parse GPX file.
"""
from lxml import etree

from srtm import SrtmLayer

XMLNS = 'http://www.topografix.com/GPX/1/1'
TRKPT_PATH = '{%s}trk/{%s}trkseg/{%s}trkpt' % (XMLNS, XMLNS, XMLNS)
    
class GPXFile(object):
    """
    Simplifies operations on GPX files. 
    """
    _data = None
    _srtm = SrtmLayer()

    def __init__(self, fileobj):
        """
        Parse GPX file to ElementTree instance.
        """
        self._data = etree.parse(fileobj)

    def fix_elevation(self):
        """
        Replace elevation from GPX by data from SRTM.
        """
        for trkpt in self._data.findall(TRKPT_PATH):
            lat = float(trkpt.attrib['lat'])
            lon = float(trkpt.attrib['lon'])
            
            ele = trkpt.find('{%s}ele' % XMLNS)
            if ele is not None:
                ele.text = str(self._srtm.get_elevation(lat, lon))
                
    def remove_extensions(self):
        """
        Remove 'extensions' tags for GPX file.
        """
        def _remove_extensions(parent):
            ext = parent.find('{%s}extensions' % XMLNS)
            if ext is not None:
                parent.remove(ext)
        
        metadata = self._data.find('{%s}metadata' % XMLNS)
        if metadata is not None:
            _remove_extensions(metadata)
            
        for trkpt in self._data.findall(TRKPT_PATH):
            _remove_extensions(trkpt)
    
    def remove_whitespaces(self):
        """
        Remove whitespaces between tags.
        """
        for i in self._data.getiterator():
            if i.text and i.text.isspace():
                i.text = None
            if i.tail and i.tail.isspace():
                i.tail = None

    def write(self, file, pretty_print=False):
        """
        Save GPX file.
        """
        return self._data.write(file, 
                                encoding=self._data.docinfo.encoding, 
                                xml_declaration=True, 
                                pretty_print=pretty_print)
