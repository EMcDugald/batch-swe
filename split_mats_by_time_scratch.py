import scipy.io as sio
import os
import numpy as np

fname = "agg_8_sims_0_time_ss_2_ss_unstruct_ntimes_1608_wd_short"
data = sio.loadmat(os.getcwd()+"/matData/"+fname+".mat")
num_times_total, num_pixels, num_channels = np.shape(data['zt'])
times_per_sim = data['data_times'][0][0]
num_time_blocks = 4
num_sims = 8
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
    for j in range(num_sims):
        if i == 0:
            target_start_idx = max(0, target_start_idx)
            target_end_idx = max(0, target_start_idx) + int(num_frames / num_sims)
            source_start_idx = j*times_per_sim
            source_end_idx = source_start_idx + int(num_frames / num_sims)
            zt[target_start_idx:target_end_idx, :, :] = data['zt'][source_start_idx:source_end_idx, :, :]
            print(i)
            print("Target",target_start_idx,target_end_idx)
            print("Source", source_start_idx, source_end_idx)
            target_start_idx += int(num_frames / num_sims)
        else:
            target_start_idx = max(0, target_start_idx)
            target_end_idx = max(0, target_start_idx) + int(num_frames / num_sims)
            source_start_idx = (int(times_per_sim/num_time_blocks)+1)+j*(times_per_sim+1) + (i-1)*int(times_per_sim/num_time_blocks)
            source_end_idx = source_start_idx + int(num_frames / num_sims)
            zt[target_start_idx:target_end_idx, :, :] = data['zt'][source_start_idx:source_end_idx, :, :]
            print(i)
            print("Target", target_start_idx, target_end_idx)
            print("Source", source_start_idx, source_end_idx)
            target_start_idx += int(num_frames / num_sims)

    time_end += int(num_frames/num_sims)
    mat_file = os.getcwd() + "/matData/" + fname + "_tf_{}".format(time_end)+".mat"
    data_times = int(len(zt)/num_sims)*np.ones(num_sims)
    mdict = {"longitude": data['longitude'], "latitude": data['latitude'],
             "ismask": data['ismask'],
             "zt": zt, "ocn_floor": data['ocn_floor'],
             "sensor_loc_indices": data['sensor_loc_indices'],
             "sensor_locs": data['sensor_locs'], "data_times": data_times}
    sio.savemat(mat_file, mdict)
    times_per_sim = data['data_times'][0][0]








