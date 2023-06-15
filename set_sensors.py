import os
import scipy.io as sio
import pandas as pd
import numpy as np
import random
from scipy import spatial
import sys

from warnings import filterwarnings
filterwarnings(action='ignore', category=DeprecationWarning, message='`np.bool` is a deprecated alias')

proj = os.getcwd()
data_dir = os.listdir(proj+"/matData")
data_dir.sort()
fnum = 1
fname = data_dir[fnum]
data = sio.loadmat(proj+"/matData"+"/"+fname)
lons = data['longitude'][0,:]
lats = data['latitude'][0,:]
loc_arr = np.array([lons,lats]).T

real_data_file = "DART_locs.csv"
buoys_df = pd.read_csv(proj+"/csvData/"+real_data_file, sep=',')
real_lons = buoys_df['latitude'].to_numpy()
real_lats = buoys_df['longitude'].to_numpy()
buoy_loc_arr = np.array([real_lons,real_lats]).T

#num_samples = sys.argv[1]
num_samples = 15
total_num_sensors = len(buoy_loc_arr)
selection_space = [i for i in range(total_num_sensors)]
selection = random.sample(selection_space,num_samples)
selected_real_sensor_locs = buoy_loc_arr[selection]

indices = []
distances = []
for loc in selected_real_sensor_locs:
    loc_arr[spatial.KDTree(loc_arr).query(loc)[1]]
    distance, index = spatial.KDTree(loc_arr).query(loc)
    indices.append(index)
    distances.append(distance)








