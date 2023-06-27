from netCDF4 import Dataset as netcdf_dataset
import scipy.io as sio
import os
import sys
import pandas as pd
import numpy as np

from warnings import filterwarnings
filterwarnings(action='ignore', category=DeprecationWarning, message='`np.bool` is a deprecated alias')

epi_long = (float(sys.argv[1])*np.pi)/180.
epi_lat = (float(sys.argv[2])*np.pi)/180.
nc_file = os.getcwd()+"/cdfData/initial_condition.nc"
nc_data = netcdf_dataset(nc_file)
lons = nc_data.variables['lonCell'][:].data
lats = nc_data.variables['latCell'][:].data
#coords = np.array([lons,lats]).T
min_idx = (np.sqrt((lons-epi_long)**2+(lats-epi_lat)**2)).argmin()
#nearest_neighbor = coords[min_idx]
depths = nc_data['ocn_thickness'][:].data
depth = depths[min_idx]
if depth < 1000.:
    print("True")
else:
    print("False")




