from netCDF4 import Dataset as netcdf_dataset
import scipy.io as sio
import os
import sys

from warnings import filterwarnings
filterwarnings(action='ignore', category=DeprecationWarning, message='`np.bool` is a deprecated alias')

nc_path = os.getcwd()+"/cdfData/"
mat_path = os.getcwd()+"/matData"
ctr = sys.argv[1]
epi_long = sys.argv[2]
epi_lat = sys.argv[3]
nc_file = os.path.join(nc_path, str(ctr) + "_" + str(epi_long) + "_" + str(epi_lat) + ".nc")
mat_file = os.path.join(mat_path, str(ctr) + "_" + str(epi_long) + "_" + str(epi_lat) + ".mat")
dataset = netcdf_dataset(nc_file)
lons = dataset.variables['lonCell'][:].data
lats = dataset.variables['latCell'][:].data
zt = dataset.variables['zt_cell'][:].data
ke = dataset.variables['ke_cell'][:].data
mdict = {"longitude": lons, "latitude": lats, "zt": zt, "ke": ke}
sio.savemat(mat_file,mdict)
