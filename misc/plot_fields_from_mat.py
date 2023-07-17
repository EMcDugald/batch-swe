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
for i in range(len(data_dir)-1):
    fidx = i
    fname = data_dir[fidx]
    data = sio.loadmat(proj+"/matData"+"/"+fname)
    # if "agg" in fname:
    #     continue

    if 'struct' in fname and 'unstruct' not in fname:
        lons = (data['longitude'])*180./np.pi
        lats = (data['latitude'])*180./np.pi
        lons = lons.flatten()
        lats = lats.flatten()
    else:
        lons = (data['longitude'][0,:])*180./np.pi
        lats = (data['latitude'][0,:])*180./np.pi

    lons = np.where(180<lons,lons-360.,lons)
    z = data['zt']
    sensor_locs = data['sensor_locs'].T

    if 'struct' in fname and 'unstruct' not in fname:
        sensor_lons = sensor_locs[1] * 180. / np.pi
        sensor_lons = np.where(180 < sensor_lons, sensor_lons - 360., sensor_lons)
        sensor_lats = sensor_locs[0] * 180. / np.pi
    else:
        sensor_lons = sensor_locs[0]*180./np.pi
        sensor_lons = np.where(180 < sensor_lons, sensor_lons - 360., sensor_lons)
        sensor_lats = sensor_locs[1]*180./np.pi

    if "agg" in fname:
        times = np.arange(0,len(z),1).tolist()
        sampled_times = range(len(times))[::round(len(times) / 6)]
    else:
        times= data['t']
        sampled_times = range(len(times[0]))[::round(len(times[0]) / 6)]
    #fig, axs = plt.subplots(nrows=3, ncols=2,subplot_kw={'projection': ccrs.PlateCarree()})
    fig, axs = plt.subplots(nrows=3, ncols=2)
    for ax,t in zip(axs.flat, sampled_times):
        #ax.coastlines(resolution='50m', color='black', linewidth=1)
        #field = ax.tricontourf(lons, lats, z[t][:,0], cmap='bwr', alpha=.5, transform=ccrs.PlateCarree())
        if 'struct' in fname and 'unstruct' not in fname:
            zplt = z[t].flatten()
        else:
            zplt = z[t][:,0]
        field = ax.scatter(lons, lats, c=zplt, cmap='bwr')
        ax.scatter(sensor_lons, sensor_lats,color='k',s=.1)
        ax.set_title("t="+str(t))
        plt.colorbar(field,ax=ax)
    #fig.colorbar(field,ax=axs.ravel().tolist(),location='right')
    fig.set_figheight(int(3*(2+1)))
    fig.set_figwidth(int(2*(4+1)))
    plt.tight_layout()
    savepath = proj+"/figs/fields/"+fname.replace(".mat",".png")
    plt.savefig(savepath)
    plt.close()



