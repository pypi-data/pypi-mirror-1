# -*- coding: utf-8 -*-
"""
Command line tools useful to manipulate GPX files.
"""
import sys
from os.path import basename
from optparse import OptionParser

from fixer import GPXFile

def main():
    """
    Entry point for gpxtools.
    """
    parser = OptionParser(usage='%prog [options]')
    parser.add_option('-i', '--intput', dest='input', help='name of GPX input file, if not set stdin will be used', metavar='FILE')
    parser.add_option('-o', '--output', dest='output', help='name of GPX output file, if not set stdout will be used', metavar='FILE')
    
    (options,args) = parser.parse_args()

    input_f = sys.stdin
    if options.input:
        input_f = open(options.input, 'r')

    gpx_file = GPXFile(input_f)
    
    operations = {
        'gpx-fix-elevation': gpx_file.fix_elevation,
        'gpx-cleanup': gpx_file.remove_extensions,
        'gpx-compress': gpx_file.remove_whitespaces,
        }
    
    operation = basename(sys.argv[0])
    if operation not in operations:
        parser.error('unknown operation, should be one of: %s' % ', '.join(sorted(operations.keys())))
    
    ## run choosen operation
    operations[operation]()

    output_f = sys.stdout
    if options.output:
        output_f = open(options.output, 'w')

    gpx_file.write(output_f)
    output_f.close()
