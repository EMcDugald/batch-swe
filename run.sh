#!/bin/bash


num_runs=3
mesh_file="cfdData/mesh_w_elev_cvt_7.nc"
init_file="cfdData/initial_condition.nc"
delete_nc=false

for ((i=1; i<=$num_runs; i++))
do
    echo "Running scripts - Iteration $i"
#    params=$(python random_input_generator.py)
    params=$(python3 -c 'from solver/epi_sample import get_epi; print(get_epi())')
    IFS=' ' read -r epi_long epi_lat <<< "$params"

    echo "i: $i"
    echo "epi_long: $epi_long"
    echo "epi_lat: $epi_lat"

    # Run ltc.py to get initial condition. We will keep this file name fixed, and delete it before the next run
    python solver/ltc.py --mesh-file=$mesh_file \
    --init-file=$init_file \
    --radius=6371220. \
    --test-case=2 \
    --wave-xmid=$epi_long \
    --wave-ymid=$epi_lat

    # Run swe.py on the initial condition. This will generate a .mat file identified with the epicenter and num_run
    python solver/swe.py --mpas-file=$init_file \
     --time-step=300. \
     --num-steps=120 \
     --save-freq=10 \
     --stat-freq=10 \
     --loglaw-z0=0.0025 \
     --loglaw-lo=0.0010 \
     --loglaw-hi=1.0 \
     --du-damp-2=2.250E+04 \
     --counter = i \
     --wave-xmid=$epi_long \
     --wave-ymid=$epi_lat

    out_nc="cfdData/"+i+"_"+$epi_long+"_"+$epi_lat

    # Delete initial condition file before next run
    rm $init_file
    # Delete nc file if desired
    if [ "$delete_nc" = true ]; then
        rm $out_nc
    fi
done