import scipy.io as sio
import os
import numpy as np

pref = os.getcwd()
files = os.listdir(pref+"/matData")
files.sort()
data0 = sio.loadmat(pref+"/matData/"+files[0])
longitude = data0['longitude']
latitude = data0['latitude']
sensor_loc_indices = data0['sensor_loc_indices']
zt_full = data0['zt']
time_steps, pixels, ch = np.shape(zt_full)
epis = []
epi_long = files[0].split("_")[1]
epi_lat = files[0].split("_")[2].replace(".mat","")
epis.append((epi_long,epi_lat))
for i in range(1,len(files)-1):
    print(i)
    mat = sio.loadmat(pref+"/matData/"+files[i])
    zt = mat['zt']
    epi_long = files[i].split("_")[1]
    epi_lat = files[i].split("_")[2]
    zt_full = np.vstack((zt_full,zt))
    epis.append((epi_long,epi_lat))

mat_file = os.getcwd()+"/matData/"+"agg_data_0623.mat"
mdict = {"longitude": longitude, "latitude": latitude,
         "zt": zt_full, "sensor_loc_indices": sensor_loc_indices}
sio.savemat(mat_file,mdict)


