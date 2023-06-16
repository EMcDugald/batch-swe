from netCDF4 import Dataset as netcdf_dataset
import scipy.io as sio
import os
import sys
import pandas as pd
import numpy as np

from warnings import filterwarnings
filterwarnings(action='ignore', category=DeprecationWarning, message='`np.bool` is a deprecated alias')

print("Making mat file")
nc_path = os.getcwd()+"/cdfData/"
mat_path = os.getcwd()+"/matData"
ctr = sys.argv[1]
epi_long = sys.argv[2]
epi_lat = sys.argv[3]
nc_file = os.path.join(nc_path, str(ctr) + "_" + str(epi_long) + "_" + str(epi_lat) + ".nc")
mat_file = os.path.join(mat_path, str(ctr) + "_" + str(epi_long) + "_" + str(epi_lat) + ".mat")
dataset = netcdf_dataset(nc_file)
lons = dataset.variables['lonCell'][:].data
lats = dataset.variables['latCell'][:].data
zt = dataset.variables['zt_cell'][:].data
ke = dataset.variables['ke_cell'][:].data
du_cell = dataset.variables['du_cell'][:].data

real_data_file = "DART_locs.csv"
buoys_df = pd.read_csv(os.getcwd()+"/csvData/"+real_data_file, sep=',')
buoys_df['corrected_lons'] = buoys_df['longitude'].apply(lambda x: 360.+x if x<0 else x)
real_lats = buoys_df['latitude'].to_numpy()*np.pi/180.
real_lons = buoys_df['corrected_lons'].to_numpy()*np.pi/180.
buoy_loc_arr = np.array([real_lons,real_lats]).T

data_locs = np.array([lons,lats]).T
sensor_indices = []
for loc in buoy_loc_arr:
    print("data len:",len(data_locs))
    min_idx = (np.abs(data_locs-loc)).argmin()
    print("data diff len:",len(np.abs(data_locs-loc)))
    print("min idx:",min_idx)
    sensor_indices.append(min_idx)

print("max_dart_lon:",np.max(real_lons))
print("max_nc_lon:",np.max(lons))
print("DATA_Locs:", data_locs)
print("sensor_inds:",sensor_indices)
print("sample slice:", data_locs[5])
print("sample slices:", data_locs[[0,0,0,0,0,0,0,0,0,0]])
sensor_locs = data_locs[sensor_indices]




mdict = {"longitude": lons, "latitude": lats,
         "zt": zt, "ke": ke, "du_cell": du_cell,
         "sensor_indices": sensor_indices,
         "sensor_locs": sensor_locs}
sio.savemat(mat_file,mdict)

