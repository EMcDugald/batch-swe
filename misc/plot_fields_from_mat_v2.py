import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import os
import scipy.io as sio
import numpy as np
import math

from warnings import filterwarnings
filterwarnings(action='ignore', category=DeprecationWarning, message='`np.bool` is a deprecated alias')

proj = os.path.normpath(os.getcwd() + os.sep + os.pardir)
# var = 'zt'
var = 'du'
fname = "001_166.5160_-13.9660_ss_2_ntimes_776_struct_wd.mat"
data = sio.loadmat(proj+"/matData"+"/"+fname)
longitude = data['longitude']
latitude = data['latitude']
f = data[var]
if 'struct' in fname and 'unstruct' not in fname:
    sensor_lons = data['sensor_locs'][:,1]
    sensor_lats = data['sensor_locs'][:,0]
else:
    sensor_lons = data['sensor_locs'][:,0]
    sensor_lats = data['sensor_locs'][:,1]

t = 450

fig, ax = plt.subplots(nrows=1, ncols=1)
if 'struct' in fname and 'unstruct' not in fname:
    #mask_val = np.max(np.abs(f[t, :, :, 0]))
    minf = np.min(f[t, :, :, 0])
    maxf = np.max(f[t, :, :, 0])
    mask_val = min(np.abs(minf),np.abs(maxf))
    fplt = np.where((data['ismask'] == 0), f[t, :, :, 0], mask_val)
    field = ax.scatter(longitude, latitude, c=fplt, cmap='bwr',clim=[-mask_val,mask_val])
else:
    #mask_val = np.max(np.abs(f[t,:, 0]))
    minf = np.min(f[t,:,0])
    maxf = np.max(f[t,:,0])
    mask_val = min(np.abs(minf),np.abs(maxf))
    fplt = np.where((data['ismask'] == 0), f[t, :, 0], mask_val)
    field = ax.scatter(longitude, latitude, c=fplt, cmap='bwr', s=.2,clim=[-mask_val,mask_val])
ax.scatter(sensor_lons, sensor_lats,color='k',s=.5)
ax.set_title("t="+str(t))
plt.colorbar(field,ax=ax)
fig.set_figheight(4.5)
fig.set_figwidth(7)
fig.text(0.5, 0.04, 'Longitude', ha='center')
fig.text(0.04, 0.5, 'Latitude', va='center', rotation='vertical')
fig.suptitle("Div(uh)")
savepath = proj+"/figs/fields2/"+var+"_time"+str(t)+"_"+fname.replace(".mat",".png")
plt.savefig(savepath,bbox_inches='tight')
plt.close()




