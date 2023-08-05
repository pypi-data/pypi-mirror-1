#!/usr/bin/python

# grib2 plugin written by:
# Rob Cermak (sfos.uaf.edu/cermak)
# Steve Gaffigan (sfos.uaf.edu/gaffigan)

# NOTE: print statements are primarily for debugging
# This module is entering the beta test stage, so
# expect a lot of bugs.  Our main objective is to
# get the plugin working.

# General python modules
import os.path
import urllib

# Python module grib2
from grib2 import Grib2Decode
# Python pyproj is required with grib2 module
from pyproj import Proj

# Python module mkinv, should be supplied with plugin
from mkinv import *

# Python modules with pydap
from dap import dtypes
from dap.server import BaseHandler
from dap.helper import parse_querystring

# Special stuff beyond basic plugin
from dap.responses.das import typeconvert

# Requires python module Numpy
import numpy

# This is a regular expression that should match the
# files supported by your plugin.
extensions = r""".*(grb2|GRB2|grib2).*"""  

class Handler(BaseHandler):
    def __init__(self, filepath, environ):
        """
        This method receives the full path to the
        file and the WSGI environment (you probably
        won't need this.
        """
        dir, self.filename = os.path.split(filepath)

        # Open a grib2 file and store file pointer with object
        #print "FILE REQUESTED:",filepath
        self.datafp = Grib2Decode(filepath)

        # Save response type
        req = urllib.unquote(environ.get('PATH_INFO', '').lstrip('/'))
        self.response_type = req.split('.')[-1]

        # Loads GRIB2 : Table 4.5
        # Taking defined surface type codes and turns them into
        # a portion of the variable name.
        pdt_table = load_pdt_table()

        # Create a mapping of variables to records in the grib file
        # NOTE: The file name needs to point to the right data provider.
        #       This plugin was designed around the NCEP provided model output.
        # TODO: Create a generic file with multiple centers defined.
        
        xml = load_grib2_map('/home/cermak/howto/grib2/dap/plugins/grib2/ncep.xml')
        grib2varmap = map_grib2_to_var(self.datafp, xml, pdt_table)
        self.grib2varmap = grib2varmap

        # Check filepath date with associated index file
        # if index file is older than grib file, rewrite the
        # index file.  Creating an index file will help expediate
        # the process of parsing the grib file

        # Definitely need to cheat by using an index file!

    def _parseconstraints(self, constraints=None):
        """
        This method should build the dataset according to the
        constraint expression. 
        """
        # Build dataset.
        dataset = dtypes.DatasetType(name=self.filename)
        fp = self.datafp

        # Used for debugging
        #print "IN grib2 _parseconstraints" 
        #print dir(self)
        #print dir(self.das)
        #print dir(BaseHandler)
        #print constraints

        grib2varmap = self.grib2varmap
        #print grib2varmap
        
        # display variables in alphabetical order
        grib2var_keys=grib2varmap.keys()
        grib2var_keys.sort()
        
        # Always pass long latitude and longitude information
        grib2var_keys=['lat','lon']+grib2var_keys
        grib2varmap['lon']={'units': 'degrees_east', 'long_name': 'longitude', 'standard_name': 'longitude'}
        grib2varmap['lat']={'units': 'degrees_north', 'long_name': 'latitude', 'standard_name': 'latitude'}
        
        # Grab requested variables.
        fields, queries = parse_querystring(constraints)

        response_type = self.response_type

        # DEBUGGING
        #print "RESPONSE_TYPE:",response_type
        #print "FIELDS:",fields,"QUERIES:",queries

        # Add variables to dataset here depending on
        # ``fields`` and ``queries``.
        # ...
        #print dir(self.datafp)
        #q = self.datafp.getfld(2)
        #print dir(q)
        #print q.shape,q.dtype
        #print q
        #print self.datafp.inventory

        # GLOBAL ATTRIBUTES - das only
        if response_type == 'das':
            dataset.attributes['GLOBAL'] = {}
            dataset.attributes['GLOBAL']['filename'] = self.filename

            # ASSUMPTION: Grid remains constant throughout grib file
            #             latlon grids are organized as [0,360] on lon dimension

            # Contains forecast time 
            # Set global time
            idsx = fp.idsect[0]
            #print idsx
            dataset.attributes['GLOBAL']['forecast_reference_time'] = "%04d-%02d-%02d %02d:%02d:%02d" % (idsx[5],idsx[6],idsx[7],idsx[8],idsx[9],idsx[10])

            grid_info = fp.getgridinfo(0)
            #print "GI   =",grid_info
            
            # grid size
            ny = None
            if grid_info.has_key('ny') and grid_info.has_key('nx'):
                ny, nx = grid_info['ny'], grid_info['nx']
            elif grid_info.has_key('nlats') and grid_info.has_key('nlons'):
                ny, nx = grid_info['nlats'], grid_info['nlons']
            
            # Calculate grid corners (geographic)
            lat_ul = None
            if grid_info.has_key('lat/lon first grid pt'):
                lats = None
                lat_ul, lon_ul = grid_info['lat/lon first grid pt']
            else:
                lats, lons = fp.getlatlon(0)
                lat_ul, lon_ul = lats[0,0], lons[0,0]
            if grid_info.has_key('lat/lon last grid pt'):
                lat_lr, lon_lr = grid_info['lat/lon last grid pt']
            else:
                if type(lats) == type(None):
                    lats, lons = fp.getlatlon(0)
                lat_lr, lon_lr = lats[-1,-1], lons[-1,-1]

            if grid_info.has_key('projparams') and ny !=None and lat_ul != None:
                # spatial_ref for projected grids
                projinfo = grid_info['projparams']
                spatial_ref = ''
                for k in projinfo:
                    if spatial_ref:
                        spatial_ref = '%s ' % spatial_ref
                    spatial_ref = '%s+%s=%s' % (spatial_ref, k, projinfo[k])
                # use '+a +b' instead of +R for spheroids (gdal/osr bug)
                if 'R' in projinfo.keys():
                    spatial_ref=spatial_ref.replace('+R=','+a=')
                    spatial_ref = '%s +%s=%s' % (spatial_ref, 'b', projinfo['R'])
                dataset.attributes['GLOBAL']['spatial_ref'] = spatial_ref                
            elif ny !=None and lat_ul != None:
                # use equidistant cylindrical projection (eqc)
                # for latlong grids (assuming 0,360 on lon dimension)
                lat_0=(lat_ul+lat_lr)/2.0
                # spatial_ref for latlong grids
                dataset.attributes['GLOBAL']['spatial_ref'] = '+proj=eqc +lat_ts='+str(lat_0)+' +lon_0=180 +a=6371005.076123 +b=6371005.076123'
                projinfo = {'proj': 'eqc', 'lat_ts': lat_0, 'lon_0': 180, 'a': 6371005.076123, 'b': 6371005.076123}
            
            if ny !=None and lat_ul != None:
                #print "PROJ =",projinfo
                # grid corners (meters)
                p = Proj(projinfo)
                x_ul, y_ul = p(lon_ul, lat_ul)
                x_lr, y_lr = p(lon_lr, lat_lr)
                #print p(x_ul, y_ul, inverse=True)
                
                # grid spacing (meters)
                x_inc = (x_lr-x_ul)/float(nx-1)
                y_inc = (y_lr-y_ul)/float(ny-1)
                #print '(y_inc, x_inc)=(%.4f, %.4f)' % (y_inc, x_inc)
                
                # geotransform uses the UL corner (not center) of UL cell
                x_ul = x_ul-x_inc/2.
                y_ul = y_ul-y_inc/2.
                
                if not grid_info.has_key('projparams'):
                    # eqc projection gives 10' shift to correct shift 
                    # observed in GDAL and Google by subtracting 10'
                    y_ul = y_ul - 10/60.
                
                dataset.attributes['GLOBAL']['GeoTransform'] = "%s %s %s %s %s %s" % (x_ul, x_inc, 0, y_ul, 0, y_inc)
            
            for var in grib2var_keys:
                # SHOULD WORK IN DAS, but it doesn't -- future?
                if var in fields or not fields:
                    # To set attributes, we need least some empty data
                    data = 0
                    dataset[var] = dtypes.ArrayType(name = var, data = data, type = 'f', shape = None)
                    #print dir(grib2varmap[var])
                    #print "%s" % (grib2varmap[var])
                    for attr in grib2varmap[var]:
                        if not grib2varmap[var][attr]:
                            continue                        
                        if type(grib2varmap[var][attr]) not in ['list','tuple']:
                            dataset[var].attributes[attr] = grib2varmap[var][attr]
                        elif type(grib2varmap[var][attr][0]) != str:
                            dataset[var].attributes[attr] = tuple(grib2varmap[var][attr])
                        else:
                            dataset[var].attributes[attr] = ' '.join(grib2varmap[var][attr])

        #print "RESPONSE TYPE:", response_type
        if response_type in ['dds', 'ascii', 'dods']:

            # Required for dds only 
            inv = fp.inventory
            parm = fp.parameter
            levl = fp.level
            unts = fp.units
            fctm = fp.fcsttime
        
            #sys.exit()
            # PROBLEM: Reading all data at every request is time consuming
            # SOLUTION:
            # If no fields are requested, send data shapes only
            # if fields are requested, send data and shapes
            #print "FIELDS:", fields
            grid_info = fp.getgridinfo(0)
            
            if grid_info.has_key('ny'):
                ny = grid_info['ny']
            elif grid_info.has_key('nlats'):
                ny = grid_info['nlats']
            if grid_info.has_key('nx'):
                nx = grid_info['nx']
            elif grid_info.has_key('nlons'):
                nx = grid_info['nlons']
            
            maps={}
            lats, lons = fp.getlatlon(0)
            for var in (grib2var_keys,fields)[len(fields)>0]:
                # strip prefix for fields ending in .lat or .lon
                var = (var,var.split('.')[-1])[var.split('.')[-1] in ['lat','lon']]
                
                if not fields:
                    data = 0
                elif var not in ['lat','lon']:
                    rec, fld = full_rec = grib2varmap[var]['rec']
                    data = fp.getfld(rec, ifld=fld)
                else:
                    data = (lats,lons)[var=='lon']
                    if not grid_info.has_key('projparams'):
                        data = (data[:,0], data[0,:])[var=='lon']
                
                if var in ['lat', 'lon'] and not grid_info.has_key('projparams'):
                    # lon/lat stored as 64bit for latlong grids
                    ty = 'd'
                    shape = ((ny,), (nx, ))[var=='lon']
                    dims = (('lat',),('lon',))[var=='lon']
                else:
                    # all fields are returned as Float32 arrays/grids
                    ty = 'f'
                    shape = (ny, nx)
                    dims = (('lat', 'lon'),('y', 'x'))[grid_info.has_key('projparams')]
                
                if fields:
                    slice_ = fields.get(var, slice(None))
                    data = numpy.array(data[slice_]).astype(ty)
                    shape = data.shape
                
                a = dtypes.ArrayType(name = var, data = data, type = ty, shape = shape)
                a.dimensions = dims
                if var in ['lat','lon'] and not grid_info.has_key('projparams'):
                    maps[var] = a
                    dataset[var] = a
                elif not grid_info.has_key('projparams'):
                    dataset[var] = dtypes.GridType(name = var, array = a)
                    # assuming 'lat','lon' come first
                    if not fields:
                        dataset[var].maps['lat'] = maps['lat']
                        dataset[var].maps['lon'] = maps['lon']
                    else:
                        dataset[var].maps['lat'] = dtypes.ArrayType(name = 'lat', data = lats[slice_[0],0], type = 'd', shape = tuple([shape[0]]))
                        dataset[var].maps['lat'].dimensions=('lat',)
                        dataset[var].maps['lon'] = dtypes.ArrayType(name = 'lon', data = lons[0,slice_[1]], type = 'd', shape = tuple([shape[1]]))
                        dataset[var].maps['lon'].dimensions=('lon',)
                else:
                    dataset[var] = a
        
        return dataset

    def close(self):
        """
        Close files, connections, etc.
        """
        # Close the grib2 file descriptor
        self.datafp.close()

#    def das(self, fcall):
#        print dir(fcall)
#        print "DAS called"
