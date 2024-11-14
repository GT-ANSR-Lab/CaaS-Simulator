try:
	from . import caas_sim_utils
except (ImportError, SystemError):
	import caas_sim_utils.py

topFile = "./html_templates/top.html"
bottomFile = "./html_templates/bottom.html"

# UNIVERSAL CONFIG
physical_files = ['tles/STARLINK-PT1.txt']
physical_json_file = ['json/uni_config_phy.json']

virtual_files = ['tles/STARLINK_virt1.txt', 'tles/STARLINK_virt2.txt']
virtual_json_files = ['json/uni_config_virt1.json', 'json/uni_config_virt2.json']

test_data_wrapper = caas_sim_utils.create_data_universal(virtual_files, physical_files, physical_json_file, virtual_json_files)
viz_string_wrap = satsim_solver.solve_sat_wrapper(test_data_wrapper, virtual_files, physical_files)



OUT_HTML_FILE = 'sat_wrapper_test_viz.html'
caas_sim_utils.write_viz_files(viz_string_wrap, topFile, bottomFile, OUT_HTML_FILE)

coordinates = caas_sim_utils.generate_100_coordinates_around_europe()
