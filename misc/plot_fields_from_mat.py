import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import os
import scipy.io as sio
import numpy as np
import math

from warnings import filterwarnings
filterwarnings(action='ignore', category=DeprecationWarning, message='`np.bool` is a deprecated alias')

proj = os.path.normpath(os.getcwd() + os.sep + os.pardir)
data_dir = os.listdir(proj+"/matData")
data_dir.sort()
# var = 'zt'
# mask_val = 1
var = 'du'
mask_val = 1e-3
for i in range(len(data_dir)-1):
    fidx = i
    fname = data_dir[fidx]
    data = sio.loadmat(proj+"/matData"+"/"+fname)

    longitude = data['longitude']
    latitude = data['latitude']

    #z = data['zt']
    if var in data.keys():
        f = data[var]
    else:
        continue

    if 'struct' in fname and 'unstruct' not in fname:
        sensor_lons = data['sensor_locs'][:,1]
        sensor_lats = data['sensor_locs'][:,0]
    else:
        sensor_lons = data['sensor_locs'][:,0]
        sensor_lats = data['sensor_locs'][:,1]

    if "agg" in fname:
        #times = np.arange(0,len(z),1).tolist()
        times = np.arange(0,len(f),1).tolist()
        sampled_times = range(len(times))[::round(len(times) / 6)]
    else:
        times= data['t']
        sampled_times = range(len(times[0]))[::round(len(times[0]) / 6)]
    fig, axs = plt.subplots(nrows=3, ncols=2)
    for ax,t in zip(axs.flat, sampled_times):
        if 'struct' in fname and 'unstruct' not in fname:
            #zplt = np.where((data['ismask']==0),z[t,:,:,0],1)
            #field = ax.scatter(longitude, latitude, c=zplt, cmap='bwr')
            fplt = np.where((data['ismask'] == 0), f[t, :, :, 0], mask_val)
            field = ax.scatter(longitude, latitude, c=fplt, cmap='bwr')
            print(fname,np.min(fplt),np.max(fplt))
        else:
            #zplt = np.where((data['ismask']==0),z[t,:,0],1)
            #field = ax.scatter(longitude, latitude, c=zplt, cmap='bwr',s=.2)
            fplt = np.where((data['ismask'] == 0), f[t, :, 0], mask_val)
            field = ax.scatter(longitude, latitude, c=fplt, cmap='bwr', s=.2)
            print(fname,np.min(fplt), np.max(fplt))
        ax.scatter(sensor_lons, sensor_lats,color='k',s=.5)
        ax.set_title("t="+str(t))
        plt.colorbar(field,ax=ax)
    fig.set_figheight(int(3*(2+1)))
    fig.set_figwidth(int(2*(4+1)))
    plt.tight_layout()
    savepath = proj+"/figs/fields/"+var+"_"+fname.replace(".mat",".png")
    plt.savefig(savepath)
    plt.close()



