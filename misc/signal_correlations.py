import os
import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio
from scipy.fftpack import fft, ifft
from scipy.fftpack import fftshift
import itertools


data = sio.loadmat(os.getcwd()+"/matData/001_155.1520_-7.1040.mat")
z = data['zt']
sensor_indices = data['sensor_loc_indices']
signals = z[:,sensor_indices,0].T.reshape(len(sensor_indices[0,:]),len(z))
signal_ffts = np.real(fft(signals,axis=1))

comb_list = []
for comb in itertools.combinations(range(len(signals)), 2):
    comb_list.append(comb)

corr_arr = np.zeros(shape=(len(comb_list),3))
corr_arr[:,0:2] = np.asarray(comb_list)

for i in range(len(corr_arr)):
    j = int(corr_arr[i][0])
    k = int(corr_arr[i][1])
    corr = np.sum(np.real(ifft(signal_ffts[j]*signal_ffts[k])))
    corr_arr[i][2] = corr

max_corr_ind = np.argsort(corr_arr[:,2])[-1]

