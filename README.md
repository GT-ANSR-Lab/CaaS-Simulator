# CaaS Simulator

1. Run install_packages.sh to install all the dependencies necessary, Python and pip need to be installed first.  
2. To run the code, run python3 main.py. main.py calls function in caas_sim_utils.py, which will be parsing the tles, running the optimization, and generating visualization.
    1. TLE and JSON configuration file paths need to be provided in main.py
    2. Each TLE file represents one constellation.
    3. The Starlink satellites we picked are all in tles/STARLINK-PT1.txt, note that json/STARLINK-PT1.json doesn't match this txt. 
3. The input will be validated by PyEphem, if the input is valid, a constellation will be constructed.
4. To change optimization rules and goals, modify caas_sim_solver.py. 
5. If you want to change the time for the satellite to be rendered and different locations, make sure the times are edited in all 3 locations:
    1. in caas_sim_utils.py, each function starts with create_data (create_data, create_data_universal, and create_data_per_sat)function has a start_time variable in it, edit these start_time variables; 
    2. in satellite_czml.py line 37 and line 373 (the 2 lines in satellite_czml.py with the variable start_time)
6. Visualization result written to sat_wrapper_test_viz.html, to change the file, edit main.py:23 OUT_HTML_FILE.
    1. Visualization string is written into an HTML file in caas_sim_utils.py:170 write_viz_files()
<img width="1334" alt="Simulator Flow Diagram" src="https://github.com/user-attachments/assets/d96b4859-5142-46e9-99e6-2022c2e17198">
