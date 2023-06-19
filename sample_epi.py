import pandas as pd
import numpy as np
import os


# def get_epi():
#     dir = os.getcwd()+"/csvData/"
#     fname = "eqs_gt_75_npac.csv"
#     epi_df = pd.read_csv(dir+fname, sep=',')
#     locs = np.zeros((len(epi_df), 2))
#     epi_df['corrected_lons'] = epi_df['longitude'].apply(lambda x: 360. + x if x < 0 else x)
#     locs[:, 0] = epi_df['corrected_lons'].to_numpy()
#     locs[:, 1] = epi_df['latitude'].to_numpy()
#     loc_idx = np.random.randint(0,len(epi_df)-1)
#     U1 = np.random.uniform()
#     U2 = np.random.uniform()
#     rlong = 5./54.6
#     rlat = 5./69.
#     long_sample = rlong * np.sqrt(U2) * np.cos(2 * np.pi * U1) + locs[loc_idx][0]
#     lat_sample = rlat * np.sqrt(U2) * np.sin(2 * np.pi * U1) + locs[loc_idx][1]
#     return long_sample, lat_sample


def get_lons():
    dir = os.getcwd()+"/csvData/"
    fname = "eq_gt_75_npac.csv"
    epi_df = pd.read_csv(dir+fname, sep=',')
    epi_df['corrected_lons'] = epi_df['longitude'].apply(lambda x: 360. + x if x < 0 else x)
    lons = epi_df['corrected_lons'].to_numpy()
    return lons

def get_lats():
    dir = os.getcwd()+"/csvData/"
    fname = "eq_gt_75_npac.csv"
    epi_df = pd.read_csv(dir+fname, sep=',')
    lats = epi_df['latitude'].to_numpy()
    return lats