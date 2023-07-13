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
    data_id = fname.split("_")[0]
    # if data_id in ['struct','unstruct']:
    #     continue

    lon_id = fname.split("_")[1]
    if 'restruct' in fname:
        lat_id = fname.split("_")[2].replace("_restruct.mat", "")
    else:
        lat_id = fname.split("_")[2].replace(".mat","")


    if 'restruct' in fname:
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

    if 'restruct' in fname:
        sensor_lons = sensor_locs[1] * 180. / np.pi
        sensor_lons = np.where(180 < sensor_lons, sensor_lons - 360., sensor_lons)
        sensor_lats = sensor_locs[0] * 180. / np.pi
    else:
        sensor_lons = sensor_locs[0]*180./np.pi
        sensor_lons = np.where(180 < sensor_lons, sensor_lons - 360., sensor_lons)
        sensor_lats = sensor_locs[1]*180./np.pi

    #times = np.arange(0, len(z), round(len(z) / 12.))
    times= data['t']
    #fig, axs = plt.subplots(nrows=3, ncols=2,subplot_kw={'projection': ccrs.PlateCarree()})
    fig, axs = plt.subplots(nrows=4, ncols=3)
    sampled_times = times[0][::round(len(times[0])/12)][0:12]
    lag = int(sampled_times[0])
    #for ax, t in zip(axs.flat, times[0:12]):
    for ax,t in zip(axs.flat, sampled_times):
        #ax.coastlines(resolution='50m', color='black', linewidth=1)
        #field = ax.tricontourf(lons, lats, z[t][:,0], cmap='bwr', alpha=.5, transform=ccrs.PlateCarree())
        if 'restruct' in fname:
            zplt = z[t-lag].flatten()
        else:
            zplt = z[t-lag][:,0]
        field = ax.scatter(lons, lats, c=zplt, cmap='bwr')
        ax.scatter(sensor_lons, sensor_lats,color='k',s=.1)
        ax.set_title("t="+str(t))
        plt.colorbar(field,ax=ax)
    #fig.colorbar(field,ax=axs.ravel().tolist(),location='right')
    fig.set_figheight(int(4*(2+1)))
    fig.set_figwidth(int(3*(4+1)))
    plt.tight_layout()
    savepath = proj+"/figs/fields/"+"zt_"+fname.replace(".mat","")+".png"
    # if 'restruct' in fname:
    #     savepath = proj+"/figs/fields/"+"zt_"+data_id+"_long="+str(lon_id)+"_lat="+str(lat_id)+"_restruct"+".png"
    # else:
    #     savepath = proj+"/figs/fields/"+"zt_"+data_id+"_long="+str(lon_id)+"_lat="+str(lat_id)+".png"
    plt.savefig(savepath)
    plt.close()



