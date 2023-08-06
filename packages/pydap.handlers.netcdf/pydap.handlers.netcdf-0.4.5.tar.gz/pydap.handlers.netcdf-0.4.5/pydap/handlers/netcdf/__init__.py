import os.path
import re

import numpy

from arrayterator import Arrayterator

from pydap.model import *
from pydap.handlers.lib import BaseHandler
from pydap.exceptions import OpenFileError

try:
    from Nio import open_file as nc
    extensions = re.compile(
            r"^.*\.(nc|cdf|netcdf|grb|grib|grb1|grib1|grb2|grib2|hd|hdf|he2|he4|hdfeos|ccm)$",
            re.IGNORECASE)
    var_attrs = lambda var: var.__dict__.copy()
    get_value = lambda var: var.get_value()
except ImportError:
    try:
        from pynetcdf import NetCDFFile as nc
        extensions = re.compile(
                r"^.*\.(nc|cdf|netcdf)$",
                re.IGNORECASE)
        var_attrs = lambda var: var.__dict__.copy()
        get_value = lambda var: var.getValue()
    except ImportError:
        from pupynere import NetCDFFile as nc
        extensions = re.compile(
                r"^.*\.(nc|cdf|netcdf)$",
                re.IGNORECASE)
        var_attrs = lambda var: var._attributes.copy()
        get_value = lambda var: var.getValue()


class Handler(BaseHandler):

    extensions = extensions

    def __init__(self, filepath):
        self.filepath = filepath

    def parse_constraints(self, environ):
        buf_size = int(environ.get('pydap.handlers.netcdf.buf_size', 10000))

        try:
            fp = nc(self.filepath)
        except:
            message = 'Unable to open file %s.' % self.filepath
            raise OpenFileError(message)

        dataset = DatasetType(name=os.path.split(self.filepath)[1],
                attributes={'NC_GLOBAL': var_attrs(fp)})
        for dim in fp.dimensions:
            if fp.dimensions[dim] is None:
                dataset.attributes['DODS_EXTRA'] = {'Unlimited_Dimension': dim}
                break

        fields, queries = environ['pydap.ce']
        fields = fields or [[(name, ())] for name in fp.variables]
        for var in fields:
            target = dataset
            while var:
                name, slice_ = var.pop(0)
                if (name in fp.dimensions or
                        not fp.variables[name].dimensions or
                        target is not dataset):
                    target[name] = get_var(name, fp, slice_, buf_size)
                elif var:
                    attrs = var_attrs(fp.variables[name])
                    target.setdefault(name, StructureType(name=name, attributes=attrs))
                    target = target[name]
                else:  # return grid
                    attrs = var_attrs(fp.variables[name])
                    grid = target[name] = GridType(name=name, attributes=attrs)
                    grid[name] = get_var(name, fp, slice_, buf_size)
                    slice_ = list(slice_) + [slice(None)] * (len(grid.array.shape) - len(slice_))
                    for dim, dimslice in zip(fp.variables[name].dimensions, slice_):
                        grid[dim] = get_var(dim, fp, dimslice, buf_size)

        dataset._set_id()
        dataset.close = fp.close
        return dataset


def get_var(name, fp, slice_, buf_size=10000):
    if name in fp.variables:
        var = Arrayterator(fp.variables[name], buf_size)
        if var.shape: 
            data = var[slice_]
        else:
            data = numpy.array(get_value(fp.variables[name]))
        typecode = fp.variables[name].typecode()
        dims = fp.variables[name].dimensions
        attrs = var_attrs(fp.variables[name])
    else:
        if fp.dimensions.get(name) is not None:
            size = fp.dimensions[name]
        else:
            for var in fp.variables:
                var = fp.variables[var]
                if name in fp.variables[name].dimensions:
                    size = var.shape[
                            list(fp.variables[name].dimensions).index(name)]
                    break
        data = numpy.arange(size)[slice_]
        typecode = data.dtype.char
        dims, attrs = (name,), {}

    return BaseType(name=name, data=data, shape=data.shape,
            type=typecode, dimensions=dims,
            attributes=attrs)


if __name__ == '__main__':
    import sys
    from paste.httpserver import serve

    application = Handler(sys.argv[1])
    serve(application, port=8001)
