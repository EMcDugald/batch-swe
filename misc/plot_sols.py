import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import os
import scipy.io as sio

from warnings import filterwarnings
filterwarnings(action='ignore', category=DeprecationWarning, message='`np.bool` is a deprecated alias')

for i in range(11):
    for t in [1,51,101,151,200]:
        print(i,t)
        proj = os.path.normpath(os.getcwd() + os.sep + os.pardir)
        data_dir = os.listdir(proj+"/matData")
        data_dir.sort()
        fidx = i
        fname = data_dir[fidx]
        print(fname)
        data = sio.loadmat(proj+"/matData"+"/"+fname)

        lons = data['longitude']
        lats = data['latitude']
        z = data['zt']

        lons = lons[0,:]
        lats = lats[0,:]
        zt = z[t][:,0]
        print(lons)
        print(lats)
        print(zt)

        ax1 = plt.axes(projection=ccrs.PlateCarree())
        plt.tricontourf(lons,lats,zt, cmap='bwr',alpha=.5,zorder=1,transform=ccrs.PlateCarree())
        ax1.coastlines(resolution='110m', color='black', linewidth=1, zorder=2)
        plt.colorbar()
        print(proj+"/figs/"+"zt_field_sim"+str(i+1)+"_time"+str(t)+".png")
        plt.savefig(proj+"/figs/fields/"+"zt_field_sim"+str(i+1)+"_time"+str(t)+".png")
        plt.close("all")



