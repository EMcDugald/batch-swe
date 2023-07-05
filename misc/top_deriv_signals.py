import matplotlib.pyplot as plt
import os
import scipy.io as sio
import numpy as np

from warnings import filterwarnings
filterwarnings(action='ignore', category=DeprecationWarning, message='`np.bool` is a deprecated alias')

proj = os.path.normpath(os.getcwd() + os.sep + os.pardir)
data_dir = os.listdir(proj+"/matData")
data_dir.sort()

for i in range(len(data_dir)-1):
    fidx = i
    fname = data_dir[fidx]
    data = sio.loadmat(proj+"/matData"+"/"+fname)
    sim_num = fname.split("_")[0]
    epi_long = fname.split("_")[1]
    epi_lat = fname.split("_")[2]

    z = data['zt']
    sensor_indices = data['sensor_loc_indices']
    signals = z[:,sensor_indices,0].T.reshape(len(sensor_indices[0,:]),len(z))
    t = np.arange(len(z))
    signal_derivs = signals[:,1:]-signals[:,0:-1]
    abs_deriv = np.abs(signal_derivs)
    signal_maxes = np.amax(abs_deriv, axis=1)
    signal_max_inds = signal_maxes.argsort()[-10:]

    fig, axs = plt.subplots(nrows=5,ncols=2)
    for ax, idx in zip(axs.ravel(),signal_max_inds):
        ax.plot(t, signals[idx])

    plt.savefig(proj+"/figs/signals/top_derivs/"+"top_sigs_for_sim"+sim_num+"at_epi_"+epi_long+"_"+epi_lat+".png")



