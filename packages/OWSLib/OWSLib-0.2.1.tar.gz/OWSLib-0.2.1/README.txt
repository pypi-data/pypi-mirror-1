
OWSLib
======
Package for working with OGC web map and feature services.

OWSLib provides a common API for accessing service metadata and wrappers for
GetCapabilities, GetMap, and GetFeature requests.


Dependencies
------------

Before installing, see DEPENDENCIES.txt.


Installation
------------

$ python setup.py install


Usage
-----

Find out what a WMS has to offer. Service metadata:

    >>> from owslib.wms import WebMapService
    >>> wms = WebMapService('http://wms.jpl.nasa.gov/wms.cgi', version='1.1.1')
    >>> wms.capabilities.service
    'OGC:WMS'
    >>> wms.capabilities.title
    'JPL Global Imagery Service'

Available layers:

    >>> [layer.name for layer in wms.capabilities.contents]
    ['global_mosaic', 'global_mosaic_base', 'us_landsat_wgs84', 'srtm_mag', 'daily_terra_721', 'daily_aqua_721', 'daily_terra_ndvi', 'daily_aqua_ndvi', 'daily_terra', 'daily_aqua', 'BMNG', 'modis', 'huemapped_srtm', 'srtmplus', 'worldwind_dem', 'us_ned', 'us_elevation', 'us_colordem']

Details of a layer:

    >>> wms.capabilities.getContentByName('global_mosaic').title
    'WMS Global Mosaic, pan sharpened'
    >>> wms.capabilities.getContentByName('global_mosaic').boundingBox
    >>> wms.capabilities.getContentByName('global_mosaic').boundingBoxWGS84
    (-180.0, -60.0, 180.0, 84.0)
    >>> wms.capabilities.getContentByName('global_mosaic').crsOptions
    ['EPSG:4326', 'AUTO:42003']
    >>> wms.capabilities.getContentByName('global_mosaic').styles
    {'pseudo_bright': {'title': 'Pseudo-color image (Uses IR and Visual bands, 542 mapping), gamma 1.5'}, 'pseudo': {'title': '(default) Pseudo-color image, pan sharpened (Uses IR and Visual bands, 542 mapping), gamma 1.5'}, 'visual': {'title': 'Real-color image, pan sharpened (Uses the visual bands, 321 mapping), gamma 1.5'}, 'pseudo_low': {'title': 'Pseudo-color image, pan sharpened (Uses IR and Visual bands, 542 mapping)'}, 'visual_low': {'title': 'Real-color image, pan sharpened (Uses the visual bands, 321 mapping)'}, 'visual_bright': {'title': 'Real-color image (Uses the visual bands, 321 mapping), gamma 1.5'}}

Available methods, their URLs, and available formats:

    >>> [op.name for op in wms.capabilities.operations]
    ['GetCapabilities', 'GetMap']
    >>> wms.capabilities.getOperationByName('GetMap').methods
    {'Get': {'url': 'http://wms.jpl.nasa.gov/wms.cgi?'}}
    >>> wms.capabilities.getOperationByName('GetMap').formatOptions
    ['image/jpeg', 'image/png', 'image/geotiff', 'image/tiff']

That's everything needed to make a request for imagery:

    >>> img = wms.getmap(   layers=['global_mosaic'],
    ...                     styles=['visual_bright'],
    ...                     srs='EPSG:4326',
    ...                     bbox=(-112, 36, -106, 41),
    ...                     size=(300, 250),
    ...                     format='image/jpeg',
    ...                     transparent=True
    ...                     )
    >>> out = open('jpl_mosaic_visb.jpg', 'wb')
    >>> out.write(img.read())
    >>> out.close()

A very similar API exists for WebFeatureService. See
tests/MapServerWFSCapabilities.txt for details.


Known Issues
------------

OWSLib works with WMS version 1.1.1 and WFS 1.0.0 Other versions are not
supported at this time.


Support
-------

OWSLib shares a wiki and email list with the Python Cartographic Library:

http://lists.gispython.org/mailman/listinfo/community
http://trac.gispython.org/projects/PCL/wiki

Updated project information can be found at

http://trac.gispython.org/projects/PCL/wiki/OwsLib


