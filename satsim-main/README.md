# sat-sched-optimize-visualize

1. Run install_packages.sh to install all the dependencies necessary. 
2. To run the code, run main.py. main.py calls function in wrapper_calculation.py, which will be parsing, running optimization, and generating visualization.
    1. TLE and JSON configuration need to be provided in main.py
    2. Each TLE file represents one constellation.
    3. The Starlink satellites we picked are all in tles/STARLINK-PT1.txt, note that json/STARLINK-PT1.json doesn't match this txt. 
3. The input will be validated by PyEphem, if the input is valid, a constellation will be constructed.
4. To change optimization rules and goals, modify satsim_solver.py. 
5. If you want to change the time for the satellite to be rendered and different locations, make sure the times are edited in all 3 locations:
    1. in wrapper_calculation.py, each create_data... function has a start_time, change that; 
    2. in satellite_czml.py line 37 and line 373 (the 2 lines in satellite_czml.py with start_time)
6. To change the number of orbits shown, go to orbit.py:33 (the if-statement condition). 
7. Visualization result written to sat_wrapper_test_viz.html, to change the file, edit main.py:53 OUT_HTML_FILE.
    1. Visualization string is written into an HTML file in util.py:109 write_viz_files()
<img width="1334" alt="Screenshot 2024-10-16 at 10 39 01 PM" src="https://github.com/user-attachments/assets/d96b4859-5142-46e9-99e6-2022c2e17198">
