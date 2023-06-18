#!/bin/bash

#lon_arr=("204.9985" "185.5075" "179.3502" "144.801" "140.4931" "125.308" "149.3" "150.453" "173.497" "216.968" "266.1007")
#lat_arr=("19.33" "-15.6278" "-18.4743" "12.982" "27.8386" "25.125" "44.663" "51.086" "53.113" "56.953" "15.0222")

lon_arr=("204.9985" "185.5075" "179.3502" "144.801" "140.4931")
lat_arr=("19.33" "-15.6278" "-18.4743" "12.982" "27.8386")
num_runs=${#lon_arr[@]}
echo "num_runs: $num_runs"
mesh_file="cdfData/mesh_w_elev_cvt_7.nc"
init_file="cdfData/initial_condition.nc"
delete_nc=$1 #pass 1 if you want to save .nc files, 0 otherwise


for ((i=1; i<=$num_runs; i++))
do
    echo "Running scripts - Iteration $i"
    epi_long=${lon_arr[i-1]}
    epi_lat=${lat_arr[i-1]}

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
     --time-step=216. \
     --num-steps=100 \
     --save-freq=2 \
     --stat-freq=100 \
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