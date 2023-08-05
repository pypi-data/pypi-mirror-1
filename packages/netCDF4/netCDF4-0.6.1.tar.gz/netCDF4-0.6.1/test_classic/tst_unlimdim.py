import sys
import unittest
import os
import tempfile
import numpy as NP
from numpy.random.mtrand import uniform 
from numpy.testing import assert_array_equal, assert_array_almost_equal
import netCDF4_classic as netCDF4

# test creating variables with unlimited dimensions,
# writing to and retrieving data from such variables.

# create an n1dim by n2dim by n3dim random array
n1dim = 4
n2dim = 10
n3dim = 8
ranarr = 100.*uniform(size=(n1dim,n2dim,n3dim))
FILE_NAME = tempfile.mktemp(".nc")

class UnlimdimTestCase(unittest.TestCase):

    def setUp(self):
        self.file = FILE_NAME
        f  = netCDF4.Dataset(self.file, 'w')
        # foo has a single unlimited dimension
        f.createDimension('n1', n1dim)
        f.createDimension('n2', None)
        f.createDimension('n3', n3dim)
        foo = f.createVariable('data1', ranarr.dtype.str[1:], ('n1','n2','n3'))
        # write some data to it.
        foo[:,0:n2dim,:] = ranarr
        f.close()

    def tearDown(self):
        # Remove the temporary files
        os.remove(self.file)

    def runTest(self):
        """testing unlimited dimensions"""
        f  = netCDF4.Dataset(self.file, 'r')
        foo = f.variables['data1']
        # check shape.
        self.assert_(foo.shape == (n1dim,n2dim,n3dim))
        # check data.
        assert_array_almost_equal(foo[:,:,:], ranarr)
        f.close()

if __name__ == '__main__':
    unittest.main()
