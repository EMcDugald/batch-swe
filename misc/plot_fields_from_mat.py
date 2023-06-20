import matplotlib.pyplot as plt
import cartopy.crs as ccrs
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
    data_id = fname.split("_")[0]
    lon_id = fname.split("_")[1]
    lat_id = fname.split("_")[2]

    lons = (data['longitude'][0,:])*180./np.pi
    lats = (data['latitude'][0,:])*180./np.pi
    lons = np.where(180<lons,lons-360.,lons)
    z = data['zt']
    print(np.min(lons),np.max(lons))

    times = np.arange(0, len(z), round(len(z) / 5.))
    fig, axs = plt.subplots(nrows=3, ncols=2,subplot_kw={'projection': ccrs.PlateCarree()})
    for ax, t in zip(axs.flat, times):
        ax.coastlines(resolution='110m', color='black', linewidth=2)
        field = ax.tricontourf(lons, lats, z[t][:,0], cmap='bwr', alpha=.5, transform=ccrs.PlateCarree())
        ax.set_title("t="+str(t))
    fig.colorbar(field,ax=axs.ravel().tolist())
    plt.savefig(proj+"/figs/fields/"+"zt_"+data_id+"_long="+str(lon_id)+"_lat="+str(lat_id)+".png")



