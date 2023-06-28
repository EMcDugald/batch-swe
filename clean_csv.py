from netCDF4 import Dataset as netcdf_dataset
import os
import pandas as pd
import numpy as np

from warnings import filterwarnings
filterwarnings(action='ignore', category=DeprecationWarning, message='`np.bool` is a deprecated alias')


nc_file = os.getcwd()+"/ref_files/initial_condition.nc"
nc_data = netcdf_dataset(nc_file)
lons = nc_data.variables['lonCell'][:].data
lats = nc_data.variables['latCell'][:].data
depths = nc_data['ocn_thickness'][:].data
def ocean_depth(long,lat):
    min_idx = (np.sqrt((lons - long) ** 2 + (lats - lat) ** 2)).argmin()
    depth = depths[min_idx]
    return depth



dir = os.getcwd()+"/csvData/"
fname = "eq_gt_7-npac.csv"
epi_df = pd.read_csv(dir+fname, sep=',')
epi_df['corrected_lons'] = epi_df['longitude'].apply(lambda x: 360. + x if x < 0 else x)
epi_df['long_rad'] = epi_df['corrected_lons']*np.pi/180.
epi_df['lat_rad'] = epi_df['latitude']*np.pi/180.
epi_df['ocean_depth'] = epi_df.apply(lambda row: ocean_depth(row['long_rad'],row['lat_rad']),axis=1)
epi_df_cleaned = epi_df[epi_df.ocean_depth >= 1000]
epi_df_cleaned.to_csv('csvData/eq_gt_7_depth_gt_1000_npac.csv')

