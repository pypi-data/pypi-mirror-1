from __future__ import division

"""Plugin for grib files.

TODO: the plugin should convert variables of typecode 'c' to 
strings, dropping the last dimension (and possibly becoming
a BaseType)."""

__author__ = "Roberto De Almeida <rob@pydap.org>"

import os.path

from cdms import open

from arrayterator import arrayterator

from dap import dtypes
from dap.server import BaseHandler
from dap.exceptions import OpenFileError
from dap.helper import parse_querystring

extensions = r"""^.*\.(ctl|CTL)$"""

# How many records to read each time.
BUFFER = 10000


class Handler(BaseHandler):
    def __init__(self, filepath, environ):
        """Handler constructor.
        """
        self.filepath = filepath
        self.environ = environ
        
        dir, self.filename = os.path.split(filepath)
        try:
            self._file = open(filepath)
        except:
            message = 'Unable to open file %s.' % filepath
            raise OpenFileError(message)

        # Add description.
        self.description = self._file.__dict__.get('title', self.filename)

    def _parseconstraints(self, constraints=None):
        """Dataset builder.

        This method build the dataset according to the constraint
        expression. Dimensions in the grib file are treated as arrays,
        and other variables as grids.
        """
        # Build the dataset.
        dataset = dtypes.DatasetType(name=self.filename)
        attrs = dict([(k, v) for (k, v) in self._file.__dict__.items() if type(v) in [basestring, str, int, float, long]])
        dataset.attributes['NC_GLOBAL'] = attrs

        # Add DODS_EXTRA for Unlimited dimensions.
        for dim, length in self._file.dimensions.items():
            if length is None:
                dataset.attributes['DODS_EXTRA'] = {'Unlimited_Dimension': dim}
                break  # only one unlimited dimension.

        # Grab requested variables.
        fields, queries = parse_querystring(constraints)

        # Get all grids from the file.
        grids = [name for name in self._file.variables if name not in self._file.dimensions]

        # Add requested grids.
        for name in grids:
            if name in fields or not fields:
                # Instantiate the grid.
                grid = self._file.variables[name]
                slice_ = fields.get(name, slice(None))
                data = arrayterator(grid, nrecs=BUFFER)[slice_]

                a = dataset[name] = dtypes.ArrayType(name=name, data=data, shape=data.shape, dimensions=grid.listdimnames(), type=grid.typecode())
                attrs = dict([(k, v) for (k, v) in grid.__dict__.items() if type(v) in [basestring, str, int, float, long]])
                g = dataset[name] = dtypes.GridType(name=name, array=a, attributes=attrs)

                # Add missing slices so we can iterate over for each map.
                if len(slice_) < len(grid.shape):
                    slice_ += (slice(None),) * (len(grid.shape) - len(slice_))

                # Build maps.
                for mapname, mapslice, mapshape in zip(grid.listdimnames(), slice_, grid.shape):
                    map_ = self._file.getAxis(mapname)
                    data = map_[:][mapslice]  # axis behave strangely with slices, so convert to array first.
                    shape = data.shape
                    type_ = map_.typecode()
                    attrs = dict([(k, v) for (k, v) in map_.__dict__.items() if type(v) in [basestring, str, int, float, long]])
                    g.maps[mapname] = dtypes.ArrayType(name=mapname, data=data, shape=shape, type=type_, attributes=attrs)
            # Partial grids -- returned as structures.
            elif name in [var.split('.')[0] for var in fields]:
                struct_ = dataset[name] = dtypes.StructureType(name=name)
                for varname in [var.split('.')[-1] for var in fields if var.split('.')[0] == name]:
                    if varname in self._file.variables:
                        var = self._file.variables[varname]
                        data = arrayterator(var, nrecs=BUFFER)
                    else:
                        var = self._file.getAxis(varname)
                        data = var[:]
                    slice_ = fields.get("%s.%s" % (name, varname))
                    if slice_: data = data[slice_]
                    attrs = dict([(k, v) for (k, v) in var.__dict__.items() if type(v) in [basestring, str, int, float, long]])
                    struct_[varname] = dtypes.ArrayType(name=varname, data=data, shape=data.shape, type=var.typecode(), attributes=attrs)

        # Add requested dimensions.
        for name in self._file.dimensions:
            if name in fields or not fields:
                array_ = self._file.getAxis(name)
                data = array_[:]
                slice_ = fields.get(name)
                if slice_: data = data[slice_]
                attrs = dict([(k, v) for (k, v) in array_.__dict__.items() if type(v) in [basestring, str, int, float, long]])
                dataset[name] = dtypes.ArrayType(name=name, data=data, shape=data.shape, type=array_.typecode(), attributes=attrs)

        # Sort keys according to the requested order.
        if fields:
            reqs = [var.split('.')[0] for var in fields]
            dataset._keys.sort(key=lambda s: reqs.index(s))

        return dataset
                    
    def close(self):
        """Close the grib file."""
        self._file.close()
