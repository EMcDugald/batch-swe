import scipy.io as sio
import os
import numpy as np
import sys

regrid = int(sys.argv[1])
subsample_fctr = int(sys.argv[2])
num_times = int(sys.argv[3])
num_sims = int(sys.argv[4])

pref = os.getcwd()
files = os.listdir(pref+"/matData_temp")
files.sort()

data0 = sio.loadmat(pref+"/matData_temp/"+files[0])
long = data0['longitude']
lat = data0['latitude']
zb = data0['ocn_floor']
sensor_loc_indices = data0['sensor_loc_indices']
zt_full = data0['zt']
time_steps, *pixels, ch = np.shape(zt_full)
for i in range(1,len(files)):
    print(i)
    mat = sio.loadmat(pref+"/matData_temp/"+files[i])
    zt = mat['zt']
    zt_full = np.vstack((zt_full,zt))

f1 = str(num_sims)
if regrid:
    f2 = "struct"
else:
    f2 = 'unstruct'
f3 = str(subsample_fctr)
f4 = str(num_times)

mat_file = os.getcwd()+"/matData/"+"agg_"+f1+"_sims_"+f4+"_times_"+f3+"_ss_"+f2+".mat"
mdict = {"longitude": long, "latitude": lat,
         "zt": zt_full, "ocn_floor": zb,"sensor_loc_indices": sensor_loc_indices}
sio.savemat(mat_file,mdict)


for f in files:
    os.remove(pref+"/matData_temp/"+f)


