import matplotlib.pyplot as plt
from netCDF4 import Dataset as netcdf_dataset
import numpy as np
import cartopy.crs as ccrs
import os

from warnings import filterwarnings
filterwarnings(action='ignore', category=DeprecationWarning, message='`np.bool` is a deprecated alias')

proj = os.path.normpath(os.getcwd() + os.sep + os.pardir)
fname = "out_tsunami_cvt_7.nc"

print(proj+"/cfdData/"+fname)
dataset = netcdf_dataset(proj+"/cfdData/"+fname)

lats = dataset.variables['latCell'][:]
lons = dataset.variables['lonCell'][:]
zt = dataset.variables['zt_cell'][5,:,0]

ax1 = plt.axes(projection=ccrs.PlateCarree())
plt.tricontourf(lons,lats, zt, alpha=.5,zorder=1,transform=ccrs.PlateCarree())
ax1.coastlines(resolution='50m', color='black', linewidth=1)
plt.colorbar()
plt.savefig(proj+"/figs/"+"zt_field_1.png")

lon_lower = np.min(lons)
lon_upper = np.max(lons)
lat_lower = np.min(lats)
lat_upper = np.max(lats)
lonsi = np.linspace(lon_lower,lon_upper,1000)
latsi = np.linspace(lat_lower,lat_upper,1000)
import matplotlib.tri as tri
triang = tri.Triangulation(lons, lats)
interpolator = tri.LinearTriInterpolator(triang, zt)
Lonsi, Latsi = np.meshgrid(lonsi, latsi)
zti = interpolator(Lonsi, Latsi)

ax = plt.axes(
    projection=ccrs.PlateCarree()
)

plt.contourf(lonsi, latsi, zti, 60, alpha=.5,
             transform=ccrs.PlateCarree())

ax.coastlines(resolution='110m', color='white', linewidth=2)

plt.savefig(proj+"/figs/"+"zt_field_2.png")


fig = plt.figure()
ax1 = fig.add_axes([0.01, 0.01, 0.98, 0.98],projection=ccrs.PlateCarree())
ax1.coastlines(resolution='50m', color='black', linewidth=1)
ax1.set_extent([lon_lower, lon_upper, lat_lower, lat_upper])
ax1.contourf(lonsi,latsi,zti,transform=ccrs.PlateCarree())
plt.savefig(proj+"/figs/"+"zt_field_3.png")