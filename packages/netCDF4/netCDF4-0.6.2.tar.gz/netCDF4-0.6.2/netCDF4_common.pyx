__version__ = "0.6.2"

# Initialize numpy
import os
import numpy as NP
import cPickle
from numpy import __version__ as _npversion
if _npversion.split('.')[0] < '1':
    raise ImportError('requires numpy version 1.0rc1 or later')
import_array()
include "netCDF4.pxi"

def _get_att_names(int grpid, int varid):
    """Private function to get all the attribute names in a group"""
    cdef int ierr, numatts, n
    cdef char namstring[NC_MAX_NAME+1]
    if varid == NC_GLOBAL:
        ierr = nc_inq_natts(grpid, &numatts)
    else:
        ierr = nc_inq_varnatts(grpid, varid, &numatts)
    if ierr != NC_NOERR:
        raise RuntimeError(nc_strerror(ierr))
    attslist = []
    for n from 0 <= n < numatts:
        ierr = nc_inq_attname(grpid, varid, n, namstring)
        if ierr != NC_NOERR:
            raise RuntimeError(nc_strerror(ierr))
        attslist.append(namstring)
    return attslist

def _get_att(int grpid, int varid, name):
    """Private function to get an attribute value given its name"""
    cdef int ierr, n
    cdef size_t att_len
    cdef char *attname
    cdef nc_type att_type
    cdef ndarray value_arr
    cdef char *strdata 
    attname = PyString_AsString(name)
    ierr = nc_inq_att(grpid, varid, attname, &att_type, &att_len)
    if ierr != NC_NOERR:
        raise RuntimeError(nc_strerror(ierr))
    # attribute is a character or string ...
    if att_type == NC_CHAR or att_type == NC_STRING:
        value_arr = NP.empty(att_len,'S1')
        ierr = nc_get_att_text(grpid, varid, attname, <char *>value_arr.data)
        if ierr != NC_NOERR:
            raise RuntimeError(nc_strerror(ierr))
        pstring = value_arr.tostring()
        if pstring and pstring[0] == '\x80': # a pickle string
            attout = cPickle.loads(pstring)
            # attout should always be an object array.
            # if result is a scalar array, just return scalar.
            if attout.shape == (): 
                return attout.item()
            # if result is an object array with multiple elements, return a list.
            else:
                return attout.tolist()
        else:
            # remove NULL characters from python string
            return pstring.replace('\x00','')
    # a regular numeric type.
    else:
        if att_type == NC_LONG:
            att_type = NC_INT
        if att_type not in _nctonptype.keys():
            raise ValueError, 'unsupported attribute type'
        value_arr = NP.empty(att_len,_nctonptype[att_type])
        ierr = nc_get_att(grpid, varid, attname, value_arr.data)
        if ierr != NC_NOERR:
            raise RuntimeError(nc_strerror(ierr))
        if value_arr.shape == ():
            # return a scalar for a scalar array
            return value_arr.item()
        elif att_len == 1:
            # return a scalar for a single element array
            return value_arr[0]
        else:
            return value_arr

def _set_default_format(object format='NETCDF4',object verbose=False):
    """Private function to set the netCDF file format"""
    if format == 'NETCDF4':
        if verbose:
            print "Switching to netCDF-4 format"
        nc_set_default_format(NC_FORMAT_NETCDF4, NULL)
    elif format == 'NETCDF4_CLASSIC':
        if verbose:
            print "Switching to netCDF-4 format (with NC_CLASSIC_MODEL)"
        nc_set_default_format(NC_FORMAT_NETCDF4_CLASSIC, NULL)
    elif format == 'NETCDF3_64BIT':
        if verbose:
            print "Switching to 64-bit offset format"
        nc_set_default_format(NC_FORMAT_64BIT, NULL)
    elif format == 'NETCDF3_CLASSIC':
        if verbose:
            print "Switching to netCDF classic format"
        nc_set_default_format(NC_FORMAT_CLASSIC, NULL)
    else:
        raise ValueError, "format must be 'NETCDF4', 'NETCDF4_CLASSIC', 'NETCDF3_64BIT', or 'NETCDF3_CLASSIC', got '%s'" % format

def _get_format(int grpid):
    """Private function to get the netCDF file format"""
    cdef int ierr, formatp
    ierr = nc_inq_format(grpid, &formatp)
    if ierr != NC_NOERR:
        raise RuntimeError(nc_strerror(ierr))
    if formatp == NC_FORMAT_NETCDF4:
        return 'NETCDF4'
    elif formatp == NC_FORMAT_NETCDF4_CLASSIC:
        return 'NETCDF4_CLASSIC'
    elif formatp == NC_FORMAT_64BIT:
        return 'NETCDF3_64BIT'
    elif formatp == NC_FORMAT_CLASSIC:
        return 'NETCDF3_CLASSIC'

def _set_att(int grpid, int varid, name, value):
    """Private function to set an attribute name/value pair"""
    cdef int i, ierr, lenarr, n
    cdef char *attname, *datstring, *strdata
    cdef ndarray value_arr 
    attname = PyString_AsString(name)
    # put attribute value into a numpy array.
    value_arr = NP.array(value)
    # if array is 64 bit integers, cast to 32 bit integers.
    if value_arr.dtype.str[1:] == 'i8' and 'i8' not in _supportedtypes:
        value_arr = value_arr.astype('i4')
    # if array contains strings, write a text attribute.
    if value_arr.dtype.char == 'S':
        dats = value_arr.tostring()
        datstring = dats
        lenarr = len(dats)
        ierr = nc_put_att_text(grpid, varid, attname, lenarr, datstring)
        if ierr != NC_NOERR:
            raise RuntimeError(nc_strerror(ierr))
    # an object array, save as pickled string in a text attribute.
    # will be unpickled when attribute is accessed..
    elif value_arr.dtype.char == 'O':
        pstring = cPickle.dumps(value_arr,2)
        lenarr = len(pstring)
        strdata = PyString_AsString(pstring)
        ierr = nc_put_att_text(grpid, varid, attname, lenarr, strdata)
    # a 'regular' array type ('f4','i4','f8' etc)
    else:
        if value_arr.dtype.str[1:] not in _supportedtypes:
            raise TypeError, 'illegal data type for attribute, must be one of %s, got %s' % (_supportedtypes, value_arr.dtype.str[1:])
        xtype = _nptonctype[value_arr.dtype.str[1:]]
        lenarr = PyArray_SIZE(value_arr)
        ierr = nc_put_att(grpid, varid, attname, xtype, lenarr, value_arr.data)
        if ierr != NC_NOERR:
            raise RuntimeError(nc_strerror(ierr))
