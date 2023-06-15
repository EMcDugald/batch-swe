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
print(data_dir)
num_datasets = len(data_dir)-1
real_data_file = "DART_locs.csv"
buoys_df = pd.read_csv(proj+"/csvData/"+real_data_file, sep=',')
real_lons = buoys_df['latitude'].to_numpy()
real_lats = buoys_df['longitude'].to_numpy()
buoy_loc_arr = np.array([real_lons,real_lats]).T
total_num_sensors = len(buoy_loc_arr)

for j in range(num_datasets):
    fnum = j
    fname = data_dir[fnum]
    data = sio.loadmat(proj+"/matData"+"/"+fname)
    lons = data['longitude'][0,:]
    lats = data['latitude'][0,:]
    loc_arr = np.array([lons,lats]).T
    print(fname)

    #num_samples = sys.argv[1]
    #num_samples = 15
    num_samples = random.randint(5,total_num_sensors)
    print(num_samples)
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

    senseiver_locs = loc_arr[indices]
    mdict = {'sensor_loc_idx': indices,'senseiver_locs': senseiver_locs}
    sio.savemat(proj+"/locData/"+str(fname), mdict)










