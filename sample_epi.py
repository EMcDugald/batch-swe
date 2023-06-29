import pandas as pd
import os
import random
import numpy as np

def get_lons():
    dir = os.getcwd()+"/csvData/"
    fname = "eq_gt_7_depth_gt_1000_npac.csv"
    epi_df = pd.read_csv(dir+fname, sep=',')
    epi_df['corrected_lons'] = epi_df['longitude'].apply(lambda x: 360. + x if x < 0 else x)
    lons = epi_df['corrected_lons'].to_numpy()
    float_formatter = "{:.4f}".format
    np.set_printoptions(formatter={'float_kind': float_formatter})
    return lons

def get_lats():
    dir = os.getcwd()+"/csvData/"
    fname = "eq_gt_7_depth_gt_1000_npac.csv"
    epi_df = pd.read_csv(dir+fname, sep=',')
    lats = epi_df['latitude'].to_numpy()
    float_formatter = "{:.4f}".format
    np.set_printoptions(formatter={'float_kind': float_formatter})
    return lats

def get_ids(n):
    dir = os.getcwd() + "/csvData/"
    fname = "eq_gt_7_depth_gt_1000_npac.csv"
    epi_df = pd.read_csv(dir + fname, sep=',')
    return str(random.sample(range(len(epi_df)),int(n)))
