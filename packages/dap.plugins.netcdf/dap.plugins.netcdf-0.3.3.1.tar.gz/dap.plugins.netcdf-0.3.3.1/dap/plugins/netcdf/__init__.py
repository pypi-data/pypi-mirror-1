from __future__ import division

"""Plugin for NetCDF files.

TODO: the plugin should convert variables of typecode 'c' to 
strings, dropping the last dimension (and possibly becoming
a BaseType)."""

__author__ = "Roberto De Almeida <rob@pydap.org>"

import os.path

try:
    from pynetcdf import NetCDFFile
except ImportError:
    from pupynere import NetCDFFile

from arrayterator import arrayterator

from dap import dtypes
from dap.server import BaseHandler
from dap.exceptions import OpenFileError
from dap.helper import parse_querystring

extensions = r"""^.*\.(nc|NC|cdf|CDF)$"""

# How many records to read each time.
BUFFER = 10000


class Handler(BaseHandler):
    def __init__(self, filepath, environ):
        self.filepath = filepath
        self.environ = environ
        
        dir, self.filename = os.path.split(filepath)
        try:
            self._file = NetCDFFile(filepath)
        except:
            message = 'Unable to open file %s.' % filepath
            raise OpenFileError(message)

        # Add description.
        self.description = getattr(self._file, 'title', self.filename)

    def _parseconstraints(self, constraints=None):
        """Dataset builder.

        This method build the dataset according to the constraint
        expression. Dimensions in the netCDF file are treated as arrays,
        and other variables as grids.

        """
        # Build the dataset.
        dataset = dtypes.DatasetType(name=self.filename)
        dataset.attributes['NC_GLOBAL'] = self._file.__dict__.copy()

        # Add DODS_EXTRA for Unlimited dimensions.
        for dim, length in self._file.dimensions.items():
            if length is None:
                dataset.attributes['DODS_EXTRA'] = {'Unlimited_Dimension': dim}
                break  # only one unlimited dimension.

        # Grab requested variables.
        fields, queries = parse_querystring(constraints)

        # Get all grids from the netCDF file.
        grids = []
        for name in self._file.variables:
            # Must not be a dimension.
            if name not in self._file.dimensions:
                var = self._file.variables[name]
                for dim in var.dimensions:
                    # Check that all dimensions are defined.
                    if dim not in self._file.variables: break
                grids.append(name)

        # Add requested grids.
        for name in grids:
            if name in fields or not fields:
                # Instantiate the grid.
                grid = self._file.variables[name]
                slice_ = fields.get(name, (slice(None),))
                data = arrayterator(grid, nrecs=BUFFER)[slice_]

                if not grid.dimensions:
                    dataset[name] = dtypes.BaseType(name=name, data=grid.getValue(), type=grid.typecode(), attributes=grid.__dict__.copy())
                else:
                    a = dtypes.ArrayType(name=name, data=data, shape=data.shape, dimensions=grid.dimensions, type=grid.typecode())
                    g = dataset[name] = dtypes.GridType(name=name, array=a, attributes=grid.__dict__.copy())

                    # Add missing slices so we can iterate over for each map.
                    if len(slice_) < len(grid.shape):
                        slice_ += (slice(None),) * (len(grid.shape) - len(slice_))

                    # Build maps.
                    for mapname, mapslice, mapshape in zip(grid.dimensions, slice_, grid.shape):
                        if mapname in self._file.variables:
                            map_ = self._file.variables[mapname]
                            data = arrayterator(map_, nrecs=BUFFER)[mapslice]
                            shape = data.shape
                            type_ = map_.typecode()
                            attrs_ = map_.__dict__.copy()
                        else:
                            # Some netCDF files have dimensions without values, apparently.
                            # We just fill them with integers.
                            data = range(mapshape)
                            shape = (mapshape,)
                            type_ = 'l'
                            attrs_ = None
                        g.maps[mapname] = dtypes.ArrayType(name=mapname, data=data, shape=shape, type=type_, attributes=attrs_)
            # Partial grids -- returned as structures.
            elif name in [var.split('.')[0] for var in fields]:
                struct_ = dataset[name] = dtypes.StructureType(name=name)
                for varname in [var.split('.')[-1] for var in fields if var.split('.')[0] == name]:
                    var = self._file.variables[varname]
                    data = arrayterator(var, nrecs=BUFFER)
                    slice_ = fields.get("%s.%s" % (name, varname))
                    if slice_: data = data[slice_]
                    struct_[varname] = dtypes.ArrayType(name=varname, data=data, shape=data.shape, type=var.typecode(), attributes=var.__dict__.copy())

        # Add requested dimensions.
        for name in self._file.dimensions:
            if name in fields or not fields:
                if name not in self._file.variables:
                    # Record variable. shape is None, so we 
                    # need to get it from some variable.
                    for varname in self._file.variables:
                        var = self._file.variables[varname]
                        if name in var.dimensions:
                            i = list(var.dimensions).index(name)
                            shape = var.shape[i]
                            break
                    data = range(shape)
                    shape = (shape,)
                    dataset[name] = dtypes.ArrayType(name=name, data=data, shape=shape, type='l')
                else:
                    array_ = self._file.variables[name]
                    data = arrayterator(array_, nrecs=BUFFER)
                    slice_ = fields.get(name)
                    if slice_: data = data[slice_]
                    dataset[name] = dtypes.ArrayType(name=name, data=data, shape=data.shape, type=array_.typecode(), attributes=array_.__dict__.copy())

        # Sort keys according to the requested order.
        if fields:
            reqs = [var.split('.')[0] for var in fields]
            dataset._keys.sort(key=lambda s: reqs.index(s))

        return dataset
                    
    def close(self):
        """Close the netCDF file."""
        self._file.close()
