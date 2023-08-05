from __future__ import division

"""
Plugin for GDAL.

TODO: fix order

Based on http://home.gdal.org/~warmerda/gdal_opendap_design.html.
"""

__author__ = "Roberto De Almeida <rob@pydap.org>"

import os.path

import numpy
import gdal
from gdalconst import *

from dap import dtypes
from dap.server import BaseHandler
from dap.exceptions import OpenFileError, ConstraintExpressionError
from dap.helper import parse_querystring, fix_slice

# Handle all files inside a ``gdal`` directory.
extensions = r"""^.*/gdal/.+$"""


class Handler(BaseHandler):
    def __init__(self, filepath, environ):
        """
        Handler constructor.
        """
        self.filepath = filepath
        self.environ = environ
        
        dir, self.filename = os.path.split(filepath)
        try:
            self._file = gdal.Open(filepath)
        except:
            message = 'Unable to open file %s.' % filepath
            raise OpenFileError(message)

        # Add description.
        self.description = self._file.GetMetadata().get('title', self.filename)

    def _parseconstraints(self, constraints=None):
        """
        Dataset builder.
        """
        # Extract georeference information from file.
        ysize, xsize = shape = self._file.RasterYSize, self._file.RasterXSize
        coords = self._file.GetGeoTransform()
        
        # Build lat and lon.
        if coords[2] == 0.0:
            lon = coords[0] + numpy.arange(xsize) * coords[1]
            xunits = 'degrees_east'
        else:
            lon = numpy.arange(xsize)
            xunits = None
        if coords[4] == 0.0:
            lat = coords[3] + numpy.arange(ysize) * coords[5]
            yunits = 'degrees_north'
        else:
            lat = numpy.arange(ysize)
            yunits = None

        # Get boundaries.
        nmn, smn = coords[0], coords[0]
        if coords[1] > 0: nmn += xsize * coords[1]
        else: smn += xsize * coords[1]
        if coords[2] > 0: nmn += ysize * coords[2]
        else: smn += ysize * coords[2]
        eme, wme = coords[3], coords[3]
        if coords[4] > 0: eme += xsize * coords[4]
        else: wme += xsize * coords[4]
        if coords[5] > 0: eme += ysize * coords[5]
        else: wme += ysize * coords[5]

        # Build the dataset.
        dataset = dtypes.DatasetType(name=self.filename)
        dataset.attributes['GLOBAL'] = {'GeoTransform': ' '.join([str(v) for v in coords]),
                                        'Metadata': self._file.GetMetadata(),
                                        'Northernmost_Northing': nmn,
                                        'Southernmost_Northing': smn,
                                        'Easternmost_Easting': eme,
                                        'Westernmost_Easting': wme,
                                        'spatial_ref': self._file.GetProjectionRef(),
                                       }

        # Grab requested variables.
        fields, queries = parse_querystring(constraints)

        # Number of bands.
        bands = self._file.RasterCount

        # Fix fields by replacing ``easting`` with ``band_1.easting`` and
        # the same for ``northing``.
        if 'easting' in fields:
            if bands > 1: raise ConstraintExpressionError("Ambiguous shorthand notation request: easting")
            # Replace SHN with FQN.
            position = fields._keys.index('easting')
            fields._dict['band_1.easting'] = fields._dict['easting']
            del fields._dict['easting']
            fields._keys[position] = 'band_1.easting'

        if 'northing' in fields:
            if bands > 1: raise ConstraintExpressionError("Ambiguous shorthand notation request: northing")
            # Replace SHN with FQN.
            position = fields._keys.index('northing')
            fields._dict['band_1.northing'] = fields._dict['northing']
            del fields._dict['northing']
            fields._keys[position] = 'band_1.northing'

        # Treat each band as a grid.
        for i in range(bands):
            band = self._file.GetRasterBand(i+1)
            name = 'band_%d' % (i+1)
            if name in fields or not fields:
                type_ = gdal.GetDataTypeName(band.DataType)

                # Get region to read.
                slice_ = fields.get(name)
                if slice_ is not None:
                    slice_ = fix_slice(2, slice_)
                    y0 = getattr(slice_[0], 'start', slice_[0]) or 0
                    x0 = getattr(slice_[1], 'start', slice_[1]) or 0
                    ysize = (getattr(slice_[0], 'stop', x0+1) or band.YSize) - y0
                    xsize = (getattr(slice_[1], 'stop', x0+1) or band.XSize) - x0
                    ystep = getattr(slice_[0], 'step', 1) or 1
                    xstep = getattr(slice_[1], 'step', 1) or 1
                    lat = lat[slice_[0]]
                    lon = lon[slice_[1]]
                else:
                    x0, y0 = 0, 0
                    xsize, ysize = band.XSize, band.YSize
                    xstep = ystep = 1

                # Read data.
                data = band.ReadRaster(x0, y0, xsize, ysize, xsize, ysize, band.DataType)
                data = numpy.fromstring(data, type_)
                data.shape = (ysize, xsize)
                if slice_ is not None: data = data[(slice(None, None, ystep), slice(None, None, xstep))]

                # Attributes.
                attrs = {}
                attrs['Description'] = band.GetDescription()
                attrs['Metadata'] = band.GetMetadata()
                attrs['missing_value'] = band.GetNoDataValue()
                attrs['add_offset'] = band.GetOffset() or 0.0
                attrs['scale_factor'] = band.GetScale() or 1.0
                
                array_ = dtypes.ArrayType(name=name,
                                          data=data,
                                          shape=data.shape,
                                          dimensions=['easting', 'northing'],
                                          type=type_)
                g = dataset[name] = dtypes.GridType(name=name, array=array_, attributes=attrs)
                g.maps['easting'] = dtypes.ArrayType(name='easting',
                                                     data=lon,
                                                     shape=lon.shape,
                                                     dimensions=['easting'],
                                                     type=lon.dtype.char)
                if xunits: g.maps['easting'].attributes['units'] = xunits
                g.maps['northing'] = dtypes.ArrayType(name='northing',
                                                      data=lat,
                                                      shape=lat.shape,
                                                      dimensions=['northing'],
                                                      type=lat.dtype.char)
                if yunits: g.maps['northing'].attributes['units'] = yunits

            # Partial grids, returned as a structure.
            elif name in [var.split('.')[0] for var in fields]:
                struct_ = dataset[name] = dtypes.StructureType(name=name)
                reqs = [var.split('.')[1] for var in fields if var.split('.')[0] == name]

                if name in reqs:
                    slice_ = fields.get('%s.%s' % (name, name))
                    if slice_ is not None:
                        slice_ = fix_slice(2, slice_)
                        y0 = getattr(slice_[0], 'start', slice_[0]) or 0
                        x0 = getattr(slice_[1], 'start', slice_[1]) or 0
                        ysize = (getattr(slice_[0], 'stop', x0+1) or band.YSize) - y0
                        xsize = (getattr(slice_[1], 'stop', x0+1) or band.XSize) - x0
                        ystep = getattr(slice_[0], 'step', 1) or 1
                        xstep = getattr(slice_[1], 'step', 1) or 1
                    else:
                        x0, y0 = 0, 0
                        xsize, ysize = band.XSize, band.YSize
                        xstep = ystep = 1

                    # Read data.
                    data = band.ReadRaster(x0, y0, xsize, ysize, xsize, ysize, band.DataType)
                    type_ = gdal.GetDataTypeName(band.DataType)
                    data = numpy.fromstring(data, type_)
                    data.shape = (ysize, xsize)
                    if slice_ is not None: data = data[(slice(None, None, ystep), slice(None, None, xstep))]

                    # Attributes.
                    attrs = {}
                    attrs['Description'] = band.GetDescription()
                    attrs['Metadata'] = band.GetMetadata()
                    attrs['missing_value'] = band.GetNoDataValue()
                    attrs['add_offset'] = band.GetOffset() or 0.0
                    attrs['scale_factor'] = band.GetScale() or 1.0
                    
                    struct_[name] = dtypes.ArrayType(name=name,
                                                     data=data,
                                                     shape=data.shape,
                                                     type=type_,
                                                     attributes=attrs)

                if 'easting' in reqs:
                    slice_ = fields.get('%s.easting' % name, slice(None))
                    lon = lon[slice_]
                    struct_['easting'] = dtypes.ArrayType(name='easting',
                                                          data=lon,
                                                          shape=lon.shape,
                                                          dimensions=['easting'],
                                                          type=lon.dtype.char)
                    if xunits: struct_['easting'].attributes['units'] = xunits

                if 'northing' in reqs:
                    slice_ = fields.get('%s.northing' % name, slice(None))
                    lat = lat[slice_]
                    struct_['northing'] = dtypes.ArrayType(name='northing',
                                                          data=lat,
                                                          shape=lat.shape,
                                                          dimensions=['northing'],
                                                          type=lat.dtype.char)
                    if yunits: struct_['northing'].attributes['units'] = yunits

                # Sort keys according to the requested order.
                if struct_.keys(): struct_._keys.sort(key=lambda s: reqs.index(s))

        # Sort keys according to the requested order.
        if fields:
            reqs = [var.split('.')[0] for var in fields]
            dataset._keys.sort(key=lambda s: reqs.index(s))

        return dataset
