#!/bin/bash


num_runs=$1 #number of simulations to make
echo $num_runs
mesh_file="cdfData/mesh_w_elev_cvt_7.nc"
init_file="cdfData/initial_condition.nc"
delete_nc=$2 #pass 1 if you want to save .nc files, 0 otherwise
wait_until_first_detection=$3 #passing 1 suppresses frames until a signal above 1e-3 is discovered
suppress_zero_sigs=$4 #passing 1 eliminates sensor locations that never exceed 1e-3
regrid=$5 #passing 1 interpolates the data onto a strucured grid
subsample_fctr=$6 #passing n subsamples the output by n, ie arr[::n] or arr[::n,::n]
num_times=$7 #passing n randomly selects n time slices to keep. passing 0 keeps all times
agg_data=$8 #passing 1 aggregates all the data from the run
long_arr=($(python3 -c 'from sample_epi import get_lons; print(str(get_lons()).replace("[","").replace("]","").replace("\n",""))'))
lat_arr=($(python3 -c 'from sample_epi import get_lats; print(str(get_lats()).replace("[","").replace("]","").replace("\n",""))'))
ids=($(python3 -c 'import sys, sample_epi; print(sample_epi.get_ids(sys.argv[1]).replace("[","").replace("]","").replace(",",""))' "$num_runs"))
echo "epicenter sampling indices: ${ids[@]}"


for ((i=1; i<=$num_runs; i++))
do
    echo "Running scripts - Iteration $i"
    idx=${ids[i-1]}
    epi_long=${long_arr[$idx]}
    epi_lat=${lat_arr[$idx]}

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

    break_flag=$(python is_too_shallow.py $epi_long $epi_lat)
    if [ "$break_flag" = "True" ]; then
      rm $init_file
      echo "water too shallow at $epi_long, $epi_lat"
      continue
    fi

    # Run swe.py on the initial condition. This will generate a .mat file identified with the epicenter and num_run
    printf -v i_pad "%03d" $i
    python solver/swe.py --mpas-file=$init_file \
     --time-step=216. \
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

    python make_mat.py $i_pad $epi_long $epi_lat $wait_until_first_detection $suppress_zero_sigs $regrid $subsample_fctr $num_times $agg_data

    # Delete initial condition file before next run
    rm $init_file
    # Delete nc file if desired
    if [ "$delete_nc" = 1 ]; then
        rm $out_nc
    fi
done

if [ "$agg_data" = 1 ]; then
  python agg_mats.py $regrid $subsample_fctr $num_times $num_runs
fi
