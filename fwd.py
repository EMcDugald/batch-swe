
import netCDF4 as nc
import numpy as np
import sys

nc_file = sys.argv[1]

flow = nc.Dataset(nc_file, "a", format="NETCDF4")

dt = flow.time_step

hh_cell = np.asarray(flow["hh_cell"])
zb_cell = np.asarray(flow["zb_cell"])
uh_cell = np.asarray(flow["uh_cell"])
    
# eval. at half step, so that the predictor is 2nd-order accurate
uh_cell_mid = 0. * uh_cell
uh_cell_mid[:-1, :, :] = 0.5 * (uh_cell[:-1, : ,:] + uh_cell[1:, :, :])
    
# dh/dt + div(u*h) = 0
hf_cell = hh_cell - dt * uh_cell_mid
zt_pred = hf_cell[:, :, 0] + zb_cell
  
# move up by 1 to sync time-step
zt_pred[1:, :] = zt_pred[:-1, :]
zt_pred[0, :] = zt_pred[0, :]
    
if ("zt_pred" not in flow.variables.keys()):
    flow.createVariable(
        "zt_pred", "f4", ("Time", "nCells", "nVertLevels"))
    flow["zt_pred"].long_name = \
        "Prediction of top surface elevation"
    
flow["zt_pred"][:] = np.reshape(
    zt_pred, (zt_pred.shape[0], zt_pred.shape[1], 1))
    
flow.close()
    
    
    
