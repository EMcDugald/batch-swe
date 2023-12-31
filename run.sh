#!/bin/bash


mesh_file="cdfData/mesh_w_elev_cvt_7.nc"
init_file="cdfData/initial_condition.nc"
delete_nc=$1 #pass 1 if you want to save .nc files, 0 otherwise
epi_long_arr=($(python3 -c 'from sample_epi import get_lons; print(str(get_lons()).replace("[","").replace("]","").replace("\n",""))'))
epi_lat_arr=($(python3 -c 'from sample_epi import get_lats; print(str(get_lats()).replace("[","").replace("]","").replace("\n",""))'))
num_runs=${#epi_long_arr[@]}

for ((i=1; i<=$num_runs; i++))
do
    epi_long=${epi_long_arr[i-1]}
    epi_lat=${epi_lat_arr[i-1]}
    echo "Running scripts - Iteration $i"
    echo "i: $i"
    echo "epi_long: $epi_long"
    echo "epi_lat: $epi_lat"

    # Run ltc.py to get initial condition. We will keep this file name fixed, and delete it before the next run
    echo "mesh file: $mesh_file"
    echo "init file: $init_file"
    python solver/ltc.py --mesh-file=$mesh_file \
    --init-file=$init_file \
    --radius=6371220. \
    --test-case=2 \
    --wave-xmid=$epi_long \
    --wave-ymid=$epi_lat

    # Run swe.py on the initial condition. This will generate a .mat file identified with the epicenter and num_run
    printf -v i_pad "%03d" $i
    python solver/swe.py --mpas-file=$init_file \
     --time-step=300. \
     --num-steps=120 \
     --save-freq=2 \
     --stat-freq=2 \
     --loglaw-z0=0.0025 \
     --loglaw-lo=0.0010 \
     --loglaw-hi=1.0 \
     --du-damp-2=2.250E+04 \
     --counter=$i_pad \
     --wave-xmid=$epi_long \
     --wave-ymid=$epi_lat

    out_nc="cdfData/"$i_pad"_"$epi_long"_"$epi_lat".nc"
    echo "out nc: $out_nc"

    python make_mat.py $i_pad $epi_long $epi_lat

    # Delete initial condition file before next run
    rm $init_file
    # Delete nc file if desired
    if [ "$delete_nc" = 0 ]; then
        rm $out_nc
    fi
done