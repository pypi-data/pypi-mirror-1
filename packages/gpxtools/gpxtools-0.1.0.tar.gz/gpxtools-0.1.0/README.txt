========
gpxtools
========

Overview
========

Command line tools useful to manipulate GPX files.


Tools
=====

gpx-elevation-fix
-----------------

Fixes elevation (Z-axis) data in GPX file based on `SRTM`_ data.


gpx-cleanup
-----------

Removes from GPX file unnecessary data (e.g.: speed or course) stored by some GPS devices.


gpx-compress
------------

Removes unnecessary chars (e.g.: white spaces) to decrease GPX file size.

     
Using
=====

::

    Usage: command-name [options]
    
    Options:
      -h, --help                show this help message and exit
      -i FILE, --intput=FILE    name of GPX input file, if not set stdin will be used
      -o FILE, --output=FILE    name of GPX output file, if not set stdout will be used

Possible is also cascade joining of commands::

    cat input.gpx  | ./bin/gpx-fix-elevation | ./bin/gpx-cleanup | ./bin/gpx-compress > output.gpx


Installation
============

*gpxtools* requires `GDAL python bindings`_. This packege uses `GDAL library`_.
You can build it form source or install from binary package. 
For more details see `GDAL library`_ homepage.

*gpxtools* requires also `lxml`_. To build it you can use `plone.recipe.lxml`_ buildout recipe.

Installation with *easy_install*
--------------------------------

Run command::

    $ easy_install gpxtools


Installation with *buildout*
----------------------------

Save script in `buildout.cfg` file::

    [buildout]
    develop = .
    parts = gpxtools-script
    
    [gpxtools-script]
    recipe = zc.recipe.egg
    eggs = gpxtools

Run commands::

    $ python bootstrap.py
    $ ./bin/buildout
    
Commands will be created in *bin* subdirectory.


References
==========

* `gpxtools home page`_
* `gpxtools at pypi`_
* `GDAL python bindings`_
* `GDAL library`_
* `SRTM`_
* `lxml`_
* `plone.recipe.lxml`_

.. _gpxtools home page: http://lichota.pl/blog/topics/gpxtools
.. _gpxtools at pypi: http://pypi.python.org/pypi/gpxtools/
.. _GDAL python bindings: http://pypi.python.org/pypi/GDAL
.. _GDAL library: http://gdal.org/
.. _SRTM: http://srtm.csi.cgiar.org/
.. _lxml: http://pypi.python.org/pypi/lxml
.. _plone.recipe.lxml: http://pypi.python.org/pypi/plone.recipe.lxml


Author & Contact
================

:Author: Wojciech Lichota <``wojciech[at]lichota.pl``>

.. image:: http://lichota.pl/lichota-logo.png
