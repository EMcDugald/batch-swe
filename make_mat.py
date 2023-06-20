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
mat_path = os.getcwd()+"/matData/"
ctr = sys.argv[1]
epi_long = sys.argv[2]
epi_lat = sys.argv[3]
nc_file = os.path.join(nc_path, ctr + "_" + str(epi_long) + "_" + str(epi_lat) + ".nc")
mat_file = os.path.join(mat_path, ctr + "_" + str(epi_long) + "_" + str(epi_lat) + ".mat")
dataset = netcdf_dataset(nc_file)
sim_lons = dataset.variables['lonCell'][:].data
sim_lats = dataset.variables['latCell'][:].data
zt = dataset.variables['zt_cell'][:].data
ke = dataset.variables['ke_cell'][:].data
du_cell = dataset.variables['du_cell'][:].data

real_sensor_locs_file = "DART_locs.csv"
buoys_df = pd.read_csv(os.getcwd()+"/csvData/"+real_sensor_locs_file, sep=',')
buoys_df['corrected_lons'] = buoys_df['longitude'].apply(lambda x: 360.+x if x<0 else x)
real_lon_locs = buoys_df['corrected_lons'].to_numpy()*np.pi/180.
real_lat_locs = buoys_df['latitude'].to_numpy()*np.pi/180.
buoy_loc_arr = np.array([real_lon_locs,real_lat_locs]).T

sim_locs = np.array([sim_lons,sim_lats]).T
sensor_indices = []
for loc in buoy_loc_arr:
    min_idx = (np.sqrt((sim_locs[:,0]-loc[0])**2+(sim_locs[:,1]-loc[1])**2)).argmin()
    sensor_indices.append(min_idx)

sensor_locs = sim_locs[sensor_indices]
print("dist from actual sensors:",np.linalg.norm(sensor_locs-buoy_loc_arr))
sensor_lons = sensor_locs[:,0]
sensor_lats = sensor_locs[:,1]


mdict = {"longitude": sim_lons, "latitude": sim_lats,
         "zt": zt, "ke": ke, "du_cell": du_cell,
         "sensor_loc_indices": sensor_indices,
         "sensor_locs": sensor_locs}
sio.savemat(mat_file,mdict)


#not necessary to run this- this generates a figure to check that the selected data coordinates are close to the actual dart buoys
# import matplotlib.pyplot as plt
# import cartopy.crs as ccrs
# proj = os.getcwd()
# fig = plt.figure()
# ax2 = plt.axes(projection=ccrs.PlateCarree())
# ax2.set_global()
# ax2.coastlines(resolution='110m', color='black', linewidth=2)
# real_lon_locs = real_lon_locs*180./np.pi
# real_lat_locs = real_lat_locs*180./np.pi
# ax2.scatter(real_lon_locs,real_lat_locs,c='r',alpha=.5,transform=ccrs.PlateCarree())
# sensor_lons = sensor_lons*180./np.pi
# sensor_lats = sensor_lats*180./np.pi
# ax2.scatter(sensor_lons,sensor_lats,c='k',alpha=.5,transform=ccrs.PlateCarree())
# plt.savefig(proj+"/figs/"+"buoy_loc_estimates.png")

