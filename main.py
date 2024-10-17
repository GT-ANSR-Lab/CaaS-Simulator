try:
	from . import util
	from . import wrapper_calculation
	from . import satellite_calculation
	from . import orbit
except (ImportError, SystemError):
	import util
	import wrapper_calculation
	import satellite_calculation
	import orbit

topFile = "./html_templates/top.html"
bottomFile = "./html_templates/bottom.html"

# UNIVERSAL CONFIG
physical_files = ['tles/STARLINK-PT1.txt']
physical_json_file = ['json/uni_config_phy.json']

virtual_files = ['tles/STARLINK_virt1.txt', 'tles/STARLINK_virt2.txt']
virtual_json_files = ['json/uni_config_virt1.json', 'json/uni_config_virt2.json']

test_data_wrapper = wrapper_calculation.create_data_universal(virtual_files, physical_files, physical_json_file, virtual_json_files)
viz_string_wrap = wrapper_calculation.solve_sat_wrapper(test_data_wrapper, virtual_files, physical_files)



OUT_HTML_FILE = 'sat_wrapper_test_viz.html'
util.write_viz_files(viz_string_wrap, topFile, bottomFile, OUT_HTML_FILE)

coordinates = util.generate_100_coordinates_around_europe()
