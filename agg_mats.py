import scipy.io as sio
import os
import numpy as np
import sys

regrid = int(sys.argv[1])
subsample_fctr = int(sys.argv[2])
num_times = int(sys.argv[3])
num_sims = int(sys.argv[4])
with_div = int(sys.argv[5])
split_times = int(sys.argv[6])

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

if split_times:
    fname = "agg_"+f1+"_sims_"+f4+"_time_ss_"+f3+"_ss_"+f2+"_ntimes_"+f5+f6
    data = sio.loadmat(os.getcwd() + "/matData/" + fname + ".mat")
    num_times_total, num_pixels, num_channels = np.shape(data['zt'])
    times_per_sim = data['data_times'][0][0]
    num_time_blocks = split_times
    time_end = 0
    for i in range(num_time_blocks):
        target_start_idx = 0
        if i == 0:
            num_frames = num_sims * (int((times_per_sim - 1) / num_time_blocks) + 1)
            times_per_sim = times_per_sim
        else:
            num_frames = num_sims * (int((times_per_sim - 1) / num_time_blocks))
            times_per_sim = times_per_sim - 1
        zt = np.zeros(shape=(num_frames, num_pixels, num_channels))
        if with_div:
            du = np.zeros(shape=(num_frames, num_pixels, num_channels))
        for j in range(num_sims):
            if i == 0:
                target_start_idx = max(0, target_start_idx)
                target_end_idx = max(0, target_start_idx) + int(num_frames / num_sims)
                source_start_idx = j * times_per_sim
                source_end_idx = source_start_idx + int(num_frames / num_sims)
                zt[target_start_idx:target_end_idx, :, :] = data['zt'][source_start_idx:source_end_idx, :, :]
                if with_div:
                    du[target_start_idx:target_end_idx, :, :] = data['du'][source_start_idx:source_end_idx, :, :]
                print(i)
                print("Target", target_start_idx, target_end_idx)
                print("Source", source_start_idx, source_end_idx)
                target_start_idx += int(num_frames / num_sims)
            else:
                target_start_idx = max(0, target_start_idx)
                target_end_idx = max(0, target_start_idx) + int(num_frames / num_sims)
                source_start_idx = (int(times_per_sim / num_time_blocks) + 1) + j * (times_per_sim + 1) + (i - 1) * int(times_per_sim / num_time_blocks)
                source_end_idx = source_start_idx + int(num_frames / num_sims)
                zt[target_start_idx:target_end_idx, :, :] = data['zt'][source_start_idx:source_end_idx, :, :]
                if with_div:
                    du[target_start_idx:target_end_idx, :, :] = data['du'][source_start_idx:source_end_idx, :, :]
                print(i)
                print("Target", target_start_idx, target_end_idx)
                print("Source", source_start_idx, source_end_idx)
                target_start_idx += int(num_frames / num_sims)

        time_end += int(num_frames / num_sims)
        mat_file = os.getcwd() + "/matData/" + fname + "_tf_{}".format(time_end) + ".mat"
        data_times = int(len(zt) / num_sims) * np.ones(num_sims)
        if with_div:
            mdict = {"longitude": data['longitude'], "latitude": data['latitude'],
                     "ismask": data['ismask'],"du": du,
                     "zt": zt, "ocn_floor": data['ocn_floor'],
                     "sensor_loc_indices": data['sensor_loc_indices'],
                     "sensor_locs": data['sensor_locs'], "data_times": data_times}
        else:
            mdict = {"longitude": data['longitude'], "latitude": data['latitude'],
                    "ismask": data['ismask'],
                    "zt": zt, "ocn_floor": data['ocn_floor'],
                    "sensor_loc_indices": data['sensor_loc_indices'],
                    "sensor_locs": data['sensor_locs'], "data_times": data_times}
        sio.savemat(mat_file, mdict)
        times_per_sim = data['data_times'][0][0]



