import pandas as pd
import os
import numpy as np
import warnings
warnings.filterwarnings("ignore")


dir = os.getcwd()+"/csvData/"
fname = "eq_gt_7_depth_gt_1000_npac.csv"
epi_df = pd.read_csv(dir+fname, sep=',')
df = epi_df[epi_df['place'].str.contains("Japan",na=False)]
df = df[['place', 'corrected_lons','latitude']]
coords = np.array(list(zip(df.corrected_lons, df.latitude)))

from sklearn.cluster import KMeans

for i in range(1, 5):
    kmeans = KMeans(n_clusters=i, random_state=0)
    kmeans.fit(coords)
    print(kmeans.cluster_centers_)