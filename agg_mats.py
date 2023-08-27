import scipy.io as sio
import os
import numpy as np
import sys

regrid = int(sys.argv[1])
subsample_fctr = int(sys.argv[2])
num_times = int(sys.argv[3])
num_sims = int(sys.argv[4])
with_div = int(sys.argv[5])

pref = os.getcwd()
files = os.listdir(pref+"/matData_temp")
files.sort()

data_idx = []
data0 = sio.loadmat(pref+"/matData_temp/"+files[0])
long = data0['longitude']
lat = data0['latitude']
zb = data0['ocn_floor']
ismask = data0['ismask']
sensor_loc_indices = data0['sensor_loc_indices']
sensor_locs = data0['sensor_locs']
zt_full = data0['zt']
if with_div:
    du_full = data0['du']
time_steps = len(zt_full)
data_idx = [time_steps]
for i in range(1,len(files)):
    mat = sio.loadmat(pref+"/matData_temp/"+files[i])
    zt = mat['zt']
    zt_full = np.vstack((zt_full,zt))
    data_idx.append(len(zt))
    if with_div:
        du = mat['du']
        du_full = np.vstack((du_full,du))

f1 = str(num_sims)
if regrid:
    f2 = "struct"
else:
    f2 = 'unstruct'
f3 = str(subsample_fctr)
f4 = str(num_times)
f5 = str(len(zt_full))
if with_div:
    f6 = "_wd"
else:
    f6 = ""

mat_file = os.getcwd()+"/matData/"+"agg_"+f1+"_sims_"+f4+"_time_ss_"+f3+"_ss_"+f2+"_ntimes_"+f5+f6+".mat"

if with_div:
    mdict = {"longitude": long, "latitude": lat,
             "ismask": ismask, "du": du_full,
             "zt": zt_full, "ocn_floor": zb,
             "sensor_loc_indices": sensor_loc_indices,
            "sensor_locs": sensor_locs, "data_times": data_idx}
else:
    mdict = {"longitude": long, "latitude": lat,
             "ismask": ismask,
             "zt": zt_full, "ocn_floor": zb,
             "sensor_loc_indices": sensor_loc_indices,
             "sensor_locs": sensor_locs, "data_times": data_idx}
sio.savemat(mat_file,mdict)


for f in files:
    os.remove(pref+"/matData_temp/"+f)


