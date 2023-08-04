#!/bin/bash

lon_arr=("136.6180" "142.6190" "143.9100" "139.5560" "143.7300" "139.3290" )
lat_arr=("33.0700" "37.8120" "41.8150" "28.8560" "22.3380" "28.9320")

#lon_arr=("136.6180" "142.6190")
#lat_arr=("33.0700" "37.8120")

mesh_file="cdfData/mesh_w_elev_cvt_7.nc"
init_file="cdfData/initial_condition.nc"
delete_nc=$1 #pass 1 if you want to save .nc files, 0 otherwise
wait_until_first_detection=$2 #passing 1 suppresses frames until a signal above 1e-3 is discovered
suppress_zero_sigs=$3 #passing 1 eliminates sensor locations that never exceed 1e-3
regrid=$4 #passing 1 interpolates the data onto a strucured grid
subsample_fctr=$5 #passing n subsamples the output by n, ie arr[::n] or arr[::n,::n]
num_times=$6 #passing n randomly selects n time slices to keep. passing 0 keeps all times
agg_data=$7 #passing 1 aggregates all the data from the run
with_div=$8 #passing 1 includes velocity divergence
num_runs=${#lon_arr[@]}
echo "epicenter sampling indices: ${ids[@]}"


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
     --time-step=54. \
     --num-steps=200 \
     --save-freq=1 \
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

    python make_mat.py $i_pad $epi_long $epi_lat $wait_until_first_detection $suppress_zero_sigs $regrid $subsample_fctr $num_times $agg_data $with_div

    # Delete initial condition file before next run
    rm $init_file
    # Delete nc file if desired
    if [ "$delete_nc" = 1 ]; then
        rm $out_nc
    fi
done

if [ "$agg_data" = 1 ]; then
  python agg_mats.py $regrid $subsample_fctr $num_times $num_runs $with_div
fi