from StringIO import StringIO

from pupynere import netcdf_file

from pydap.model import *
from pydap.lib import walk
from pydap.responses.lib import BaseResponse


class NetCDFResponse(BaseResponse):
    def __init__(self, dataset):
        BaseResponse.__init__(self, dataset)
        self.headers.extend([
                ('Content-description', 'dods_netcdf'),
                ('Content-type', 'application/x-netcdf'),
                ])

    @staticmethod
    def serialize(dataset):
        buf = StringIO()
        f = netcdf_file(buf, 'w')
        
        for grid in walk(dataset, GridType):
            # Add dimensions.
            for dim, map_ in grid.maps.items():
                if dim not in f.dimensions:
                    f.createDimension(dim, map_.shape[0])
                    var = f.createVariable(dim, map_.type.typecode, (dim,))
                    var[:] = map_[:]
                    for k, v in map_.attributes.items():
                        if not isinstance(v, dict):
                            setattr(var, k, v)
            # Add the var.
            var = f.createVariable(grid.name, grid.type.typecode, grid.dimensions)
            var[:] = grid[:]
            for k, v in grid.attributes.items():
                if not isinstance(v, dict):
                    setattr(var, k, v)

        f.flush()
        return [ buf.getvalue() ]
                    

def save(dataset, filename):
    f = open(filename, 'w')
    f.write(
            NetCDFResponse(dataset).serialize(dataset)[0])
    f.close()


if __name__ == '__main__':
    import numpy

    dataset = DatasetType(name='foo')
    dataset['grid'] = GridType(name='grid')
    data = numpy.arange(6)
    data.shape = (2,3)
    dataset['grid']['array'] = BaseType(data=data, name='array', shape=data.shape, type=data.dtype.char)
    x, y = numpy.arange(2), numpy.arange(3) * 10
    dataset['grid']['x'] = BaseType(name='x', data=x, shape=x.shape, type=x.dtype.char)
    dataset['grid']['y'] = BaseType(name='y', data=y, shape=y.shape, type=y.dtype.char)
    dataset._set_id()

    save(dataset, 'test.nc')
