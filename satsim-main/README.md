# sat-sched-optimize-visualize

1. Run install_packages.sh to install all the dependencies necessary (I'm not 100% sure if that includes everything, if it doesn't let me know!). 
2. To run the code, run main.py (main.py calls functions in wrapper_calculation.py, which takes care of parsing, running optimization, and visualization). 
3. If you want to change the time for the satellite to be rendered and different locations, make sure the times are edited in all 3 locations:
    1. in wrapper_calculation.py, each create_data... function has a start_time, change that; 
    2. in satellite_czml.py line 37 and line 373 (the 2 lines in satellite_czml.py with start_time)
4. Currently, I've implemented 1) generate random lats, longs are in util.py, and 2) a function calculation of the Euclidian distance between a satellite's lats, longs, and elevation is ignored. I haven't implement the logit to optimiza or visualize coordinates. 
5. To control the number of orbits shown, go to orbit.py:33 (the if-statement condition). 
6. Visualization result is currently written to sat_wrapper_test_viz.html, to change this, edit main.py:53 OUT_HTML_FILE. 
7. The Starlink satellites we picked are all in tles/STARLINK-PT1.txt, note that json/STARLINK-PT1.json doesn't match this txt. 
<img width="1334" alt="Screenshot 2024-10-16 at 10 39 01 PM" src="https://github.com/user-attachments/assets/d96b4859-5142-46e9-99e6-2022c2e17198">
