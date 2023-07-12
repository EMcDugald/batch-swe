import scipy.io as sio
import os
import numpy as np

pref = os.getcwd()
# files = os.listdir(pref+"/matData")
# files.sort()
# files = ["001_128.4250_25.9300_ss_4_restruct.mat",
#          "002_183.7820_-20.2520_ss_4_restruct.mat",
#          "003_186.1920_-20.6800_ss_4_restruct.mat",
#          "004_286.2620_-16.5340_ss_4_restruct.mat",
#          "005_174.8958_-21.1265_ss_4_restruct.mat"]
files = ["001_167.0570_-14.5320_ss_4.mat",
         "002_143.3160_39.6350_ss_4.mat",
         "003_182.0000_48.0000_ss_4.mat",
         "004_163.3860_56.0170_ss_4.mat",
         "005_169.8710_53.4520_ss_4.mat"]
data0 = sio.loadmat(pref+"/matData/"+files[0])
long = data0['longitude']
lat = data0['latitude']
sensor_loc_indices = data0['sensor_loc_indices']
zt_full = data0['zt']
time_steps, *pixels, ch = np.shape(zt_full)
for i in range(1,len(files)):
    print(i)
    mat = sio.loadmat(pref+"/matData/"+files[i])
    zt = mat['zt']
    zt_full = np.vstack((zt_full,zt))


#mat_file = os.getcwd()+"/matData/"+"struct_agg_5sims_ss4.mat"
mat_file = os.getcwd()+"/matData/"+"unstruct_agg_5sims_ss4.mat"
mdict = {"longitude": long, "latitude": lat,
         "zt": zt_full, "sensor_loc_indices": sensor_loc_indices}
sio.savemat(mat_file,mdict)


