Note: There is a .nc mesh file required to generate the data, which is not available on this repo.
The mesh file, "mesh_w_elev_cvt_7.zip" can be found here: https://github.com/dengwirda/swe-python/releases/tag/v0.1.0.
Download this file, unzip, and place in the cdfData folder.

This repo contains code and data to generate Tsunami wave simulations based on historical epicenter locations.
The data is generated by a Shallow Water Equation solver (D Engwirda), which generates tsunami simulations based on an epicenter specification.
Historical epicenter locations can be found in csvData/eq_gt_75_npac.csv. This file contains a listing of historical earthquake epicenters with magnitude greater than 7.5, going back to 1800.
The data was generated using the USGS tool found here: https://earthquake.usgs.gov/earthquakes/map/?extent=-74.95939,-276.32813&extent=78.49055,13.35938&range=search&listOnlyShown=true&timeZone=utc&search=%7B%22name%22:%22Search%20Results%22,%22params%22:%7B%22starttime%22:%221800-01-01%2000:00:00%22,%22endtime%22:%222023-06-16%2023:59:59%22,%22maxlatitude%22:63.952,%22minlatitude%22:-22.401,%22maxlongitude%22:-65.391,%22minlongitude%22:-237.656,%22minmagnitude%22:7.5,%22eventtype%22:%22earthquake%22,%22orderby%22:%22time%22%7D%7D
Epicenters corresponding to land were manually removed from the data.
The file /csvData/DART_locs.csv contains longitude/latitude coordinates of the DART sensors, as reported here: https://www.ndbc.noaa.gov/obs.shtml?lat=13&lon=-173&zoom=2&pgm=tsunami

The data generation scripts are run.sh and run_fixed_epis.sh.
run.sh will generate 243 datasets, corresponding to 243 distinct epicenters.
run_fixed_epis.sh will generate data depending on a list of longiutde,latitude values that can be set in the script.

The scripts will call the SWE solver, which will generate .nc files. After the .nc is made, a python script is called to generate a .mat file containing the longitude/latitude coordinates, time series for the wave height, velocity divergence, and kinetic energy, and nearest longitude/latitude coordinates to the DART sensors.
If the .nc files are not needed, either script can be run with a 0/1 flag. 
Running ./run.sh 0 or ./run_fixed_epis.sh 0 will delete the .nc files. To keep the files, run with the flag set to 1.

Helpful Note: The dart buoys and epicenter locations are expressed in degrees, while the solver uses radians.
Additionally, the longitude values cooresponding to [-180,0] must be remapped to [180,360] before converting to radians.
