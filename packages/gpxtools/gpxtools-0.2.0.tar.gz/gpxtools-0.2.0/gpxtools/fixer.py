# -*- coding: utf-8 -*-
"""
Parse GPX file.
"""
from lxml import etree

from srtm import SrtmLayer
    
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
        self._xmlns = self._data.getroot().nsmap[None]
        self._trkpt_path = '{%s}trk/{%s}trkseg/{%s}trkpt' % (self._xmlns, self._xmlns, self._xmlns)

    def fix_elevation(self):
        """
        Replace elevation from GPX by data from SRTM.
        """
        for trkpt in self._data.findall(self._trkpt_path):
            lat = float(trkpt.attrib['lat'])
            lon = float(trkpt.attrib['lon'])
            
            ele = trkpt.find('{%s}ele' % self._xmlns)
            if ele is not None:
                ele.text = str(self._srtm.get_elevation(lat, lon))
            else:
                ele = etree.Element('ele')
                ele.text = str(self._srtm.get_elevation(lat, lon))
                trkpt.append(ele)

    def remove_extensions(self):
        """
        Remove 'extensions' tags for GPX file.
        """
        def _remove_extensions(parent):
            ext = parent.find('{%s}extensions' % self._xmlns)
            if ext is not None:
                parent.remove(ext)
        
        metadata = self._data.find('{%s}metadata' % self._xmlns)
        if metadata is not None:
            _remove_extensions(metadata)
            
        for trkpt in self._data.findall(self._trkpt_path):
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
