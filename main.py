try:
	from . import caas_sim_utils
	from . import caas_sim_solver
except (ImportError, SystemError):
	import caas_sim_utils
	import caas_sim_solver

# Paths to html template files
topFile = "./html_templates/top.html"
bottomFile = "./html_templates/bottom.html"

# Paths to files describing physical constellation
physical_files = ['tles/STARLINK-PT1.txt'] # array of paths to the tles files, each file represent one constellation
physical_json_file = ['json/uni_config_phy.json'] # array of paths to the config files

# Paths to files describing virtual constellation demand
virtual_files = ['tles/STARLINK_virt1.txt', 'tles/STARLINK_virt2.txt'] # array of paths to the tles files, each file represent one constellation
virtual_json_files = ['json/uni_config_virt1.json', 'json/uni_config_virt2.json'] # array of paths to the config files

# Validate and create constellation
test_data = caas_sim_utils.create_data_universal(virtual_files, physical_files, physical_json_file, virtual_json_files)

# Generate a schole based on optimization rules and goals configured in caas_sim_solver.py
viz_string_wrap = caas_sim_solver.solve_sat_wrapper(test_data, virtual_files, physical_files)


# Output Cesium based HTML file that visualizes the solver output
OUT_HTML_FILE = 'sat_wrapper_test_viz.html'
caas_sim_utils.write_viz_files(viz_string_wrap, topFile, bottomFile, OUT_HTML_FILE)