#https://earthquake.usgs.gov/earthquakes/search/
#https://www.ndbc.noaa.gov/obs.shtml?lat=13&lon=-173&zoom=2&pgm=tsunami

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import pandas as pd

proj_pref = "/Users/emcdugald/projects/aml_2023/batch-swe/"
fname = "eqs_gt_8.csv"
epi_df = pd.read_csv(proj_pref+"csvData/"+fname, sep=',')
#lats = epi_df['latitude'].to_numpy()*np.pi/180.
#lons = epi_df['longitude'].to_numpy()*np.pi/180.

lats = epi_df['latitude'].to_numpy()
lons = epi_df['longitude'].to_numpy()
mags = epi_df['mag'].to_numpy()

ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_global()
ax.coastlines(resolution='110m', color='black', linewidth=2)
im = ax.scatter(lons,lats,c=mags,cmap='viridis',alpha=.5,transform=ccrs.PlateCarree())
cb = plt.colorbar(im)
plt.savefig(proj_pref+"figs/"+"epis_1.png")

fname = "DART_locs.csv"
buoys_df = pd.read_csv(proj_pref+"csvData/"+fname, sep=',')
lats = buoys_df['latitude'].to_numpy()
lons = buoys_df['longitude'].to_numpy()

fig = plt.figure()
ax2 = plt.axes(projection=ccrs.PlateCarree())
ax2.set_global()
ax2.coastlines(resolution='110m', color='black', linewidth=2)
ax2.scatter(lons,lats,c='r',alpha=.5,transform=ccrs.PlateCarree())
plt.savefig(proj_pref+"figs/"+"buoys_1.png")
