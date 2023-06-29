#https://earthquake.usgs.gov/earthquakes/map/?extent=-74.95939,-276.32813&extent=78.49055,13.35938&range=search&listOnlyShown=true&timeZone=utc&search=%7B%22name%22:%22Search%20Results%22,%22params%22:%7B%22starttime%22:%221800-01-01%2000:00:00%22,%22endtime%22:%222023-06-16%2023:59:59%22,%22maxlatitude%22:63.952,%22minlatitude%22:-22.401,%22maxlongitude%22:-65.391,%22minlongitude%22:-237.656,%22minmagnitude%22:7.5,%22eventtype%22:%22earthquake%22,%22orderby%22:%22time%22%7D%7D
#https://www.ndbc.noaa.gov/obs.shtml?lat=13&lon=-173&zoom=2&pgm=tsunami

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import pandas as pd
import numpy as np
import os

proj = os.path.normpath(os.getcwd() + os.sep + os.pardir)
#fname = "eq_gt_75_npac.csv"
fname = "eq_gt_7_depth_gt_1000_npac.csv"
epi_df = pd.read_csv(proj+"/csvData/"+fname, sep=',')

lats = epi_df['latitude'].to_numpy()
lons = epi_df['longitude'].to_numpy()
mags = epi_df['mag'].to_numpy()
print("min epi long:",np.min(lons))
print("max epi long:",np.max(lons))
print("min epi lats:",np.min(lats))
print("max epi lats:",np.max(lats))


ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_global()
ax.coastlines(resolution='110m', color='black', linewidth=2)
im = ax.scatter(lons,lats,color='r',s=.5,transform=ccrs.PlateCarree())
cb = plt.colorbar(im)
plt.savefig(proj+"/figs/"+"epis_1.png")

fname = "DART_locs.csv"
buoys_df = pd.read_csv(proj+"/csvData/"+fname, sep=',')
lats = buoys_df['latitude'].to_numpy()
lons = buoys_df['longitude'].to_numpy()
print("min buoy long:",np.min(lons))
print("max buoy long:",np.max(lons))
print("min buoy lats:",np.min(lats))
print("max buoy lats:",np.max(lats))

fig = plt.figure()
ax2 = plt.axes(projection=ccrs.PlateCarree())
ax2.set_global()
ax2.coastlines(resolution='110m', color='black', linewidth=2)
ax2.scatter(lons,lats,c='r',alpha=.5,transform=ccrs.PlateCarree())
plt.savefig(proj+"/figs/"+"buoys_1.png")
