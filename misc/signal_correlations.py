import os
import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio
from scipy.fftpack import fft, ifft
from scipy.fftpack import fftshift
import itertools
from scipy.signal import correlate
from scipy.cluster import hierarchy


proj = os.path.normpath(os.getcwd() + os.sep + os.pardir)
print(proj)
data_dir = os.listdir(proj+"/matData")
data_dir.sort()

for i in range(len(data_dir)-1):
    fidx = i
    fname = data_dir[fidx]
    data = sio.loadmat(proj+"/matData"+"/"+fname)
    data_id = fname.split("_")[0]
    lon_id = fname.split("_")[1]
    lat_id = fname.split("_")[2].replace(".mat","")

    z = data['zt']
    sensor_indices = data['sensor_loc_indices']
    signals = z[:,sensor_indices,0].T.reshape(len(sensor_indices[0,:]),len(z))
    #signal_ffts = np.real(fft(signals,axis=1))

    comb_list = []
    for comb in itertools.combinations(range(len(signals)), 2):
        comb_list.append(comb)

    # corr_arr1 = np.zeros(shape=(len(comb_list),3))
    # corr_arr1[:,0:2] = np.asarray(comb_list)

    # for i in range(len(corr_arr1)):
    #     j = int(corr_arr1[i][0])
    #     k = int(corr_arr1[i][1])
    #     corr = np.sum(np.real(ifft(signal_ffts[j]*signal_ffts[k])))
    #     corr_arr1[i][2] = corr

    # max_corr_inds1 = np.argsort(corr_arr1[:,2])

    corr_arr2 = np.zeros(shape=(len(comb_list),3))
    corr_arr2[:,0:2] = np.asarray(comb_list)

    for i in range(len(corr_arr2)):
        j = int(corr_arr2[i][0])
        k = int(corr_arr2[i][1])
        corr = np.sum(correlate(signals[j],signals[k]))
        corr_arr2[i][2] = corr

    max_corr_inds2 = np.argsort(corr_arr2[:,2])

    mean = np.mean(corr_arr2[:, 2])
    std = np.std(corr_arr2[:, 2])
    thresh1 = mean + 3 * std
    thresh2 = mean + 4 * std
    thresh3 = mean + 5 * std
    thresh4 = np.max(corr_arr2[:, 2])
    set1 = np.where((thresh1 < corr_arr2[:, 2]) * (corr_arr2[:, 2] <= thresh2))
    set2 = np.where((thresh2 < corr_arr2[:, 2]) * (corr_arr2[:, 2] <= thresh3))
    set3 = np.where((thresh3 < corr_arr2[:, 2]) * (corr_arr2[:, 2] <= thresh4))
    sets = [set1,set2,set3]

    fig, axs = plt.subplots(nrows=3,ncols=1)
    for set,axs in zip(sets,axs.flat):
        sig_ids = []
        print("set size:",len(set[0]))
        for idx in set[0]:
            sig1_idx = int(corr_arr2[:,0][int(idx)])
            sig2_idx = int(corr_arr2[:,1][int(idx)])
            axs.plot(signals[sig1_idx])
            axs.plot(signals[sig2_idx])
            if not (sig1_idx in sig_ids):
                sig_ids.append(sig1_idx)
            if not (sig2_idx in sig_ids):
                sig_ids.append(sig2_idx)
        axs.set_title("correlations involving sigs: "+ str(sig_ids))
    fig.set_figheight(10)
    fig.set_figwidth(20)
    plt.tight_layout()
    plt.savefig(proj+"/figs/signals/correlations/"+"zt_"+data_id+"_long="+str(lon_id)+"_lat="+str(lat_id)+".png")


    from scipy.cluster import hierarchy

    # Compute the correlation matrix
    correlation_matrix = np.corrcoef(signals)

    # Apply hierarchical clustering
    linkage = hierarchy.linkage(correlation_matrix, method='average', metric='correlation')

    # Determine the number of clusters
    k = 10  # Number of desired clusters

    # Extract cluster assignments
    cluster_assignments = hierarchy.cut_tree(linkage, n_clusters=k).flatten()

    fig2, axs2 = plt.subplots(nrows=5,ncols=2)
    for i,ax2 in zip(range(k),axs2.flat):
        sig_ids = np.where((cluster_assignments==i))
        sigs_to_plot = signals[sig_ids]
        for sig in sigs_to_plot:
            ax2.plot(sig)
        ax2.set_title("cluster for sigs: " + str(sig_ids))
    fig2.set_figheight(20)
    fig2.set_figwidth(20)
    plt.tight_layout()
    plt.savefig(proj + "/figs/signals/correlations/" + "clustering zt_" + data_id + "_long=" + str(lon_id) + "_lat=" + str(lat_id) + ".png")
