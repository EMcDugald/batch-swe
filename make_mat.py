from netCDF4 import Dataset as netcdf_dataset
import scipy.io as sio
import os
import sys
import pandas as pd
import numpy as np
from scipy.interpolate import griddata
import random
import warnings
warnings.filterwarnings("ignore")
from sklearn.cluster import KMeans

from warnings import filterwarnings
filterwarnings(action='ignore', category=DeprecationWarning, message='`np.bool` is a deprecated alias')

ctr = sys.argv[1]
epi_lon = sys.argv[2]
epi_lat = sys.argv[3]
wait_until_first_detection = int(sys.argv[4])
suppress_zero_sigs = int(sys.argv[5])
regrid = int(sys.argv[6])
subsample_fctr = int(sys.argv[7])
num_times = int(sys.argv[8])
agg_data = int(sys.argv[9])
with_div = int(sys.argv[10])
artificial_sensors = int(sys.argv[11])

print("Making mat file")
nc_path = os.getcwd()+"/cdfData/"
if agg_data:
    if not os.path.exists(os.getcwd()+"/matData_temp"):
        os.mkdir(os.getcwd()+"/matData_temp")
    mat_path = os.getcwd()+"/matData_temp/"
else:
    mat_path = os.getcwd()+"/matData/"

nc_file = os.path.join(nc_path, ctr + "_" + str(epi_lon) + "_" + str(epi_lat) + ".nc")
dataset = netcdf_dataset(nc_file)

numt = dataset.dimensions['Time'].size
t = np.arange(0,numt)

real_sensor_locs_file = "DART_locs.csv"
buoys_df = pd.read_csv(os.getcwd()+"/csvData/"+real_sensor_locs_file, sep=',')
buoys_df['corrected_lons'] = buoys_df['longitude'].apply(lambda x: 360.+x if x<0 else x)
real_lon_locs = buoys_df['corrected_lons'].to_numpy()*np.pi/180.
real_lat_locs = buoys_df['latitude'].to_numpy()*np.pi/180.
buoy_loc_arr = np.array([real_lon_locs,real_lat_locs]).T
if artificial_sensors != 0:
    dir = os.getcwd() + "/csvData/"
    fname = "eq_gt_7_depth_gt_1000_npac.csv"
    epi_df = pd.read_csv(dir + fname, sep=',')
    df = epi_df[epi_df['place'].str.contains("Japan", na=False)]
    df = df[['place', 'corrected_lons', 'latitude']]
    coords = np.array(list(zip(df.corrected_lons, df.latitude)))
    kmeans = KMeans(n_clusters=artificial_sensors, random_state=0)
    kmeans.fit(coords)
    art_lons = kmeans.cluster_centers_[:,0]
    art_lats = kmeans.cluster_centers_[:,1]
    art_lons *= np.pi / 180.
    art_lats *= np.pi / 180.
    art_sens = np.array([art_lons, art_lats]).T
    buoy_loc_arr = np.vstack((buoy_loc_arr, art_sens))




if regrid:
    print("making mat file with regridding")
    num_pts = dataset.dimensions['nCells'].size
    lat_size = round(np.sqrt(num_pts/2))
    lon_size = int(2*lat_size)
    slons = np.linspace(0, 2 * np.pi, lon_size)
    slats = np.linspace(-np.pi/2,np.pi/2,lat_size)
    sim_lons, sim_lats = np.meshgrid(slons, slats)
    ulons = dataset.variables['lonCell'][:].data
    ulats = dataset.variables['latCell'][:].data
    upts = np.array([ulons,ulats]).T
    uzt = dataset.variables['zt_cell'][:].data
    #zt = np.asarray([griddata(upts,uzt[i],(sim_lons,sim_lats),method='cubic',fill_value=0) for i in range(len(uzt))])
    zt = np.asarray([griddata(upts, uzt[i], (sim_lons, sim_lats), method='nearest', fill_value=0) for i in range(len(uzt))])
    uzb = dataset.variables['zb_cell'][:].data
    #zb = np.asarray(griddata(upts, uzb, (sim_lons, sim_lats), method='cubic', fill_value=0))
    zb = np.asarray(griddata(upts, uzb, (sim_lons, sim_lats), method='nearest', fill_value=0))
    uismask = dataset.variables['is_mask'][:].data
    ismask = np.asarray(griddata(upts, uismask, (sim_lons, sim_lats), method='nearest', fill_value=0))
    if with_div:
        udu = dataset.variables['uh_cell'][:].data
        #du = np.asarray([griddata(upts, udu[i], (sim_lons, sim_lats), method='cubic', fill_value=0) for i in range(len(udu))])
        du = np.asarray([griddata(upts, udu[i], (sim_lons, sim_lats), method='nearest', fill_value=0) for i in range(len(udu))])
    sim_lons = sim_lons[::subsample_fctr,::subsample_fctr]
    sim_lats = sim_lats[::subsample_fctr,::subsample_fctr]
    zt = zt[:,::subsample_fctr,::subsample_fctr]
    zb = zb[::subsample_fctr,::subsample_fctr]
    ismask = ismask[::subsample_fctr,::subsample_fctr]
    if with_div:
        du = du[:, ::subsample_fctr, ::subsample_fctr]
    # uke = dataset.variables['ke_cell'][:].data
    # ke = np.asarray([griddata(upts,uke[i],(slons_m,slats_m),method='cubic',fill_value=0) for i in range(len(uzt))])
    # udu_cell = dataset.variables['du_cell'][:].data
    # du_cell = np.asarray([griddata(upts,udu_cell[i],(slons_m,slats_m),method='cubic',fill_value=0) for i in range(len(uzt))])
    sensor_indices = np.zeros(shape=(len(buoy_loc_arr),2),dtype=int)
    sensor_locs = np.zeros(shape=(len(buoy_loc_arr),2))
    for i, loc in zip(range(len(buoy_loc_arr)),buoy_loc_arr):
        lat_idx, lon_idx = np.unravel_index((np.sqrt((sim_lons-loc[0])**2+(sim_lats-loc[1])**2)).argmin(), sim_lats.shape)
        sensor_indices[i] = [int(lat_idx),int(lon_idx)]
        sensor_locs[i] = [sim_lats[int(lat_idx),int(lon_idx)],sim_lons[int(lat_idx),int(lon_idx)]]
    buoy_loc_arr[:, [1, 0]] = buoy_loc_arr[:, [0, 1]] #switch the column order, since lat is the row index
    print("dist from actual sensors:", np.linalg.norm(sensor_locs - buoy_loc_arr))

    # for i, loc in zip(range(len(buoy_loc_arr)),buoy_loc_arr):
    #     lon_idx, lat_idx = np.unravel_index((np.sqrt((sim_lons-loc[0])**2+(sim_lats-loc[1])**2)).argmin(), sim_lons.shape)
    #     sensor_indices[i] = [int(lon_idx),int(lat_idx)]
    #     sensor_locs[i] = [sim_lons[int(lon_idx),int(lat_idx)],sim_lats[int(lon_idx),int(lat_idx)]]
    # print("dist from actual sensors:", np.linalg.norm(sensor_locs - buoy_loc_arr))

    start = 0
    if wait_until_first_detection:
        print("waiting until first detection")
        sensor_vals = zt[:, sensor_indices[:,0], sensor_indices[:,1]]
        # 201x66 (for each time, what is the set of sensor readings. we don't consider simulations until the first time a nonzero signal is detected)
        sens_abs_max = np.max(np.abs(sensor_vals), axis=1)
        start = np.argmax(sens_abs_max > 1e-3)
        zt = zt[start:, ...]
        t = t[start:]
        if with_div:
            du = du[start:,...]

    # only save sensor indices that have non-trivial readings
    if suppress_zero_sigs:
        print("suppressing zero signal sensors")
        signals = zt[:, sensor_indices[:,0],sensor_indices[:,1]]
        # signals is (len(zt)-start,66) array. so the rows are time, cols is sig values
        # a column here gives the signal profile at a signal
        max_sigs = np.max(np.abs(signals), axis=0)
        non_zero_inds = np.where(max_sigs[:, 0] > 1e-3)
        sensor_indices = np.asarray(sensor_indices)[np.asarray(non_zero_inds).tolist()[0]].tolist()
        sensor_locs = np.zeros(shape=(len(sensor_indices), 2))
        for i in range(len(sensor_indices)):
            sensor_locs[i] = [sim_lats[sensor_indices[i][0],sensor_indices[i][1]],sim_lons[sensor_indices[i][0],sensor_indices[i][1]]]

else:
    print("making unstructured mat file")
    sim_lons = dataset.variables['lonCell'][:].data
    sim_lats = dataset.variables['latCell'][:].data
    zt = dataset.variables['zt_cell'][:].data
    zb = dataset.variables['zb_cell'][:].data
    ismask = dataset.variables['is_mask'][:].data
    sim_lons = sim_lons[::subsample_fctr]
    sim_lats = sim_lats[::subsample_fctr]
    zt = zt[:,::subsample_fctr]
    zb = zb[::subsample_fctr]
    ismask = ismask[::subsample_fctr]
    if with_div:
        du = dataset.variables['uh_cell'][:].data
        du = du[:, ::subsample_fctr]
    # ke = dataset.variables['ke_cell'][:].data
    # du_cell = dataset.variables['du_cell'][:].data

    sim_locs = np.array([sim_lons,sim_lats]).T
    sensor_indices = []
    for loc in buoy_loc_arr:
        min_idx = (np.sqrt((sim_locs[:,0]-loc[0])**2+(sim_locs[:,1]-loc[1])**2)).argmin()
        sensor_indices.append(min_idx)

    sensor_locs = sim_locs[sensor_indices]
    print("dist from actual sensors:",np.linalg.norm(sensor_locs-buoy_loc_arr))
    # sensor_lons = sensor_locs[:,0]
    # sensor_lats = sensor_locs[:,1]

    #only save data when a sensor records something nonzero, then start saving
    start=0
    if wait_until_first_detection:
        print("waiting until first detection")
        sensor_vals = zt[:,sensor_indices]
        #201x66 (for each time, what is the set of sensor readings. we don't consider simulations until the first time a nonzero signal is detected)
        sens_abs_max = np.max(np.abs(sensor_vals),axis=1)
        start = np.argmax(sens_abs_max>1e-3)
        zt = zt[start:, ...]
        t = t[start:]
        if with_div:
            du = du[start:,...]

    #only save sensor indices that have non-trivial readings
    if suppress_zero_sigs:
        print("suppressing zero signal sensors")
        signals = zt[:, sensor_indices]
        #signals is (len(zt)-start,66) array. so the rows are time, cols is sig values
        #a column here gives the signal profile at a signal
        max_sigs = np.max(np.abs(signals),axis=0)
        non_zero_inds = np.where(max_sigs[:, 0] > 1e-3)
        sensor_indices = np.asarray(sensor_indices)[np.asarray(non_zero_inds).tolist()[0]].tolist()
        sensor_locs = sim_locs[sensor_indices]


if num_times:
    all_ids = range(len(t))
    sampled_ids = random.sample(all_ids,num_times)
    t = t[sampled_ids]
    zt = zt[sampled_ids,...]
    if with_div:
        du = du[sampled_ids,...]

if regrid:
    mat_file = os.path.join(mat_path, ctr + "_" + str(epi_lon) + "_" + str(epi_lat) + "_ss_" + str(
        subsample_fctr) + "_ntimes_" + str(len(zt)) + "_struct")
else:
    mat_file = os.path.join(mat_path, ctr + "_" + str(epi_lon) + "_" + str(epi_lat) + "_ss_" + str(
        subsample_fctr) + "_ntimes_" + str(len(zt)))

if with_div:
    mat_file = mat_file + "_wd.mat"
else:
    mat_file = mat_file + ".mat"

print("number of times saved:",len(t))
if with_div:
    mdict = {"longitude": sim_lons, "latitude": sim_lats,
             "zt": zt,
             "du": du,
             "ocn_floor": zb,
            "ismask": ismask,
            # "ke": ke[start:,...],
            # "du_cell": du_cell[start:,...],
            "sensor_loc_indices": sensor_indices,
            "sensor_locs": sensor_locs,
            "t": t}
else:
    mdict = {"longitude": sim_lons, "latitude": sim_lats,
             "zt": zt,
             "ocn_floor": zb,
             "ismask": ismask,
             # "ke": ke[start:,...],
             # "du_cell": du_cell[start:,...],
             "sensor_loc_indices": sensor_indices,
             "sensor_locs": sensor_locs,
             "t": t}

sio.savemat(mat_file,mdict)


###################################################################################################################################
#not necessary to run this- this generates a figure to check that the selected data coordinates are close to the actual dart buoys
# import matplotlib.pyplot as plt
# import cartopy.crs as ccrs
# proj = os.getcwd()
# fig = plt.figure()
# ax2 = plt.axes(projection=ccrs.PlateCarree())
# ax2.set_global()
# ax2.coastlines(resolution='110m', color='black', linewidth=2)
# real_lon_locs = real_lon_locs*180./np.pi
# real_lat_locs = real_lat_locs*180./np.pi
# ax2.scatter(real_lon_locs,real_lat_locs,c='r',alpha=.5,transform=ccrs.PlateCarree())
# sensor_lons = sensor_lons*180./np.pi
# sensor_lats = sensor_lats*180./np.pi
# ax2.scatter(sensor_lons,sensor_lats,c='k',alpha=.5,transform=ccrs.PlateCarree())
# plt.savefig(proj+"/figs/"+"buoy_loc_estimates.png")

