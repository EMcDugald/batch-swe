import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import os
import scipy.io as sio
import numpy as np
import math

from warnings import filterwarnings
filterwarnings(action='ignore', category=DeprecationWarning, message='`np.bool` is a deprecated alias')

proj = os.path.normpath(os.getcwd() + os.sep + os.pardir)
#fname = "001_137.2100_32.9019_ss_2_ntimes_201_struct.mat"
fname = "001_142.5000_36.7120_ss_1_ntimes_193.mat"
data = sio.loadmat(proj+"/matData"+"/"+fname)
longitude = data['longitude']
latitude = data['latitude']
f = data['zt']
if 'struct' in fname and 'unstruct' not in fname:
    sensor_lons = data['sensor_locs'][:,1]
    sensor_lats = data['sensor_locs'][:,0]
else:
    sensor_lons = data['sensor_locs'][:,0]
    sensor_lats = data['sensor_locs'][:,1]

times = [0, 35, 70, 105, 140, 175]
min_lon = 1.760612345269236
min_lat = 0.19290481206253118
max_lon = 3.147094567168759
max_lat = 0.9645240603126557

sens_lons = sensor_lons[(min_lon < sensor_lons) & (max_lon > sensor_lons) & (min_lat < sensor_lats) & (max_lat > sensor_lats)]
sens_lats = sensor_lats[(min_lon < sensor_lons) & (max_lon > sensor_lons) & (min_lat < sensor_lats) & (max_lat > sensor_lats)]

fig, axs = plt.subplots(nrows=2, ncols=3)
if 'struct' in fname and 'unstruct' not in fname:
    mask_val = np.nan
    fplt1 = np.where((data['ismask'] == 0), f[times[0], :, :, 0], mask_val)[80:115,80:143]
    fplt2 = np.where((data['ismask'] == 0), f[times[1], :, :, 0], mask_val)[80:115,80:143]
    fplt3 = np.where((data['ismask'] == 0), f[times[2], :, :, 0], mask_val)[80:115,80:143]
    fplt4 = np.where((data['ismask'] == 0), f[times[3], :, :, 0], mask_val)[80:115,80:143]
    fplt5 = np.where((data['ismask'] == 0), f[times[4], :, :, 0], mask_val)[80:115,80:143]
    fplt6 = np.where((data['ismask'] == 0), f[times[5], :, :, 0], mask_val)[80:115,80:143]
    lats = latitude[80:115,80:143]
    lons = longitude[80:115,80:143]
    field1 = axs[0,0].scatter(lons, lats, c=fplt1)
    field2 = axs[0,1].scatter(lons, lats, c=fplt2)
    field3 = axs[0,2].scatter(lons, lats, c=fplt3)
    field4 = axs[1,0].scatter(lons, lats, c=fplt4)
    field5 = axs[1,1].scatter(lons, lats, c=fplt5)
    field6 = axs[1,2].scatter(lons, lats, c=fplt6)
    maxes = [np.nanmax(fplt1),np.nanmax(fplt2),np.nanmax(fplt3),
             np.nanmax(fplt4),np.nanmax(fplt5),np.nanmax(fplt6)]
    mins = [np.nanmin(fplt1),np.nanmin(fplt2),np.nanmin(fplt3),
             np.nanmin(fplt4),np.nanmin(fplt5),np.nanmin(fplt6)]
    maxval = max(maxes)
    minval = min(mins)
else:
    mask_val = np.nan
    fplt1 = np.where((data['ismask'] == 0), f[times[0], :, 0], mask_val)[(min_lat <= latitude) & (latitude <= max_lat) & (min_lon <= longitude) & (longitude <= max_lon)]
    fplt2 = np.where((data['ismask'] == 0), f[times[1], :, 0], mask_val)[(min_lat <= latitude) & (latitude <= max_lat) & (min_lon <= longitude) & (longitude <= max_lon)]
    fplt3 = np.where((data['ismask'] == 0), f[times[2], :, 0], mask_val)[(min_lat <= latitude) & (latitude <= max_lat) & (min_lon <= longitude) & (longitude <= max_lon)]
    fplt4 = np.where((data['ismask'] == 0), f[times[3], :, 0], mask_val)[(min_lat <= latitude) & (latitude <= max_lat) & (min_lon <= longitude) & (longitude <= max_lon)]
    fplt5 = np.where((data['ismask'] == 0), f[times[4], :, 0], mask_val)[(min_lat <= latitude) & (latitude <= max_lat) & (min_lon <= longitude) & (longitude <= max_lon)]
    fplt6 = np.where((data['ismask'] == 0), f[times[5], :, 0], mask_val)[(min_lat <= latitude) & (latitude <= max_lat) & (min_lon <= longitude) & (longitude <= max_lon)]
    lons = longitude[(min_lat <= latitude) & (latitude <= max_lat) & (min_lon <= longitude) & (longitude <= max_lon)]
    lats = latitude[(min_lat <= latitude) & (latitude <= max_lat) & (min_lon <= longitude) & (longitude <= max_lon)]
    field1 = axs[0, 0].scatter(lons, lats, c=fplt1)
    field2 = axs[0, 1].scatter(lons, lats, c=fplt2)
    field3 = axs[0, 2].scatter(lons, lats, c=fplt3)
    field4 = axs[1, 0].scatter(lons, lats, c=fplt4)
    field5 = axs[1, 1].scatter(lons, lats, c=fplt5)
    field6 = axs[1, 2].scatter(lons, lats, c=fplt6)
    maxes = [np.nanmax(fplt1), np.nanmax(fplt2), np.nanmax(fplt3),
             np.nanmax(fplt4), np.nanmax(fplt5), np.nanmax(fplt6)]
    mins = [np.nanmin(fplt1), np.nanmin(fplt2), np.nanmin(fplt3),
            np.nanmin(fplt4), np.nanmin(fplt5), np.nanmin(fplt6)]
    maxval = max(maxes)
    minval = min(mins)
field1.set_clim(minval,maxval)
field2.set_clim(minval,maxval)
field3.set_clim(minval,maxval)
field4.set_clim(minval,maxval)
field5.set_clim(minval,maxval)
field6.set_clim(minval,maxval)
axs[0,0].scatter(sens_lons, sens_lats,color='k',s=.5)
axs[0,1].scatter(sens_lons, sens_lats,color='k',s=.5)
axs[0,2].scatter(sens_lons, sens_lats,color='k',s=.5)
axs[1,0].scatter(sens_lons, sens_lats,color='k',s=.5)
axs[1,1].scatter(sens_lons, sens_lats,color='k',s=.5)
axs[1,2].scatter(sens_lons, sens_lats,color='k',s=.5)
axs[0,0].set_title("t="+str(times[0]))
axs[0,1].set_title("t="+str(times[1]))
axs[0,2].set_title("t="+str(times[2]))
axs[1,0].set_title("t="+str(times[3]))
axs[1,1].set_title("t="+str(times[4]))
axs[1,2].set_title("t="+str(times[5]))
plt.colorbar(field1,ax=axs[0,0])
plt.colorbar(field2,ax=axs[0,1])
plt.colorbar(field3,ax=axs[0,2])
plt.colorbar(field4,ax=axs[1,0])
plt.colorbar(field5,ax=axs[1,1])
plt.colorbar(field6,ax=axs[1,2])
fig.set_figheight(6)
fig.set_figwidth(12)
fig.text(0.5, 0.04, 'Longitude', ha='center')
fig.text(0.04, 0.5, 'Latitude', va='center', rotation='vertical')
fig.suptitle("Tsunami Wave Heights")
plt.tight_layout()
plt.savefig(proj + "/figs/fields/"+ fname.replace(".mat", ".png"))
plt.close()




