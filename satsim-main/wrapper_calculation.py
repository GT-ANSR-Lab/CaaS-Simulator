import math
from datetime import datetime, timedelta
import pytz
from ortools.linear_solver import pywraplp

try:
	from . import util
	from . import orbit
	from . import satsim_solver
except (ImportError, SystemError):
	import util
	import orbit
	import satsim_solver


MEAN_MOTION_REV_PER_DAY = 15.19  # Altitude ~550 km
ALTITUDE_M = 550000  # Altitude ~550 km


NUM_ORBS = 2
NUM_SATS_PER_ORB = 5
INCLINATION_DEGREE = 53
GEN_TIME = 46800
sat_objs = []
RADIUS = 10000000

EARTH_RADIUS = 6378135.0

ECCENTRICITY = 0.0000001  # Circular orbits are zero, but pyephem does not permit 0, so lowest possible value
ARG_OF_PERIGEE_DEGREE = 0.0
PHASE_DIFF = True

VIRTUAL_RADIUS = 200000.0
PHYSICAL_RADIUS = 500000.0
MARKER_RADIUS = 50000.0
MARKER_ELEVATION = 200000
COLOR_LIST = [
	"AQUA", "BROWN", "CHARTREUSE", "CORAL",
	"DEEPPINK", "FIREBRICK", "GHOSTWHITE", "GOLD", "GOLDENROD", "GREEN",
	"LAVENDER"
]

# Create data with tles information about the virtual and physical constellations
def create_data(virtual_tles, physical_tles):
	data = {}
	start_time = datetime.utcnow().replace(tzinfo=pytz.UTC) + timedelta(hours=1)
	data['epoch_str'] = start_time.strftime("%Y-%m-%d %H:%M:%S")

	data["virtual"], data["num_virtual_const"] = util.const_setup(virtual_tles)
	data["physical"], num_phys_const = util.const_setup(physical_tles)

	data["virtual_list"] = list(range(len(data["virtual"])))
	data["physical_list"] = list(range(len(data['physical'])))

	return data

# Create data with tles information about the virtual and physical constellations, 
# but uses universal config files for constellation setup
def create_data_universal(virtual_tles, physical_tles, physical_json_file, virtual_json_files):
	data = {}
	start_time = datetime.utcnow().replace(tzinfo=pytz.UTC) + timedelta(hours=1)
	data['epoch_str'] = start_time.strftime("%Y-%m-%d %H:%M:%S")

	data["virtual"], data["num_virtual_const"] = util.const_setup_universal_config(virtual_tles, virtual_json_files)
	data["physical"], num_phys_const = util.const_setup_universal_config(physical_tles, physical_json_file)

	data["virtual_list"] = list(range(len(data["virtual"])))
	data["physical_list"] = list(range(len(data['physical'])))

	return data

# Create data per satellite (with individual config files for each satellite constellation)
def create_data_per_sat(virtual_tles, physical_tles, virtual_json_file, physical_json_file):
	data = {}
	start_time = datetime.utcnow().replace(tzinfo=pytz.UTC) + timedelta(hours=1)
	data['epoch_str'] = start_time.strftime("%Y-%m-%d %H:%M:%S")

	data["virtual"], data["num_virtual_const"] = util.const_setup_per_sat_config(virtual_tles, virtual_json_file)
	data["physical"], num_phys_const = util.const_setup_per_sat_config(physical_tles, physical_json_file)

	data["virtual_list"] = list(range(len(data["virtual"])))
	data["physical_list"] = list(range(len(data['physical'])))

	return data

# Evaluate the preference of a virtual satellite to connect with a physical satellite based on distance
def eval_preference(virtual_sat, phys_sat, radius, epoch):
	distance = util.distance_m_between_satellites(virtual_sat, phys_sat, epoch, epoch)
	if distance < radius and distance >= 0: 
		return 1 - distance / radius
	return 0


# Calculate Euclidean distance between a satellite's position and a given latitude/longitude
def eval_sat_coordinate_distance(sat, lat, long):
	return math.sqrt( (sat.sublat - lat) ** 2 + (sat.sublong - long) ** 2 )


# Create a visualization string for virtual and physical satellites based on assignment data
def wrapper_visualize(data, assignment):
	viz_string = ""

	# Loop through virtual satellites and generate visualization strings
	for i in data['virtual_list']:
		data['virtual'][i]["sat_obj"].compute(data['epoch_str'])
		viz_string += "viewer.entities.add({name : '', position: Cesium.Cartesian3.fromDegrees(" \
			+ str(math.degrees(data['virtual'][i]["sat_obj"].sublong)) + ", " \
			+ str(math.degrees(data['virtual'][i]["sat_obj"].sublat)) + ", "\
			+ str(data['virtual'][i]["sat_obj"].elevation) + "), "\
			+ "ellipsoid : {radii : new Cesium.Cartesian3(" + str(VIRTUAL_RADIUS) + ", " + str(VIRTUAL_RADIUS) + ", " + str(VIRTUAL_RADIUS) + "), "
		
		# Assign color based on constellation id (cid)
		color = COLOR_LIST[data['virtual'][i]['cid']]
		
		viz_string += "material : Cesium.Color." + color + ".withAlpha(1),}});\n"

	# Determine marker positions for physical satellites
	num_const = data["num_virtual_const"]
	print('data["num_virtual_const"]', data["num_virtual_const"])
	MARKER_POS = []
	if num_const % 2 != 0:
		MARKER_POS = list(x - (num_const // 2) for x in range(num_const))
	else:
		MARKER_POS = list(x - (num_const / 2) + 0.5 for x in range(num_const)) # 0, 1 ->  -0.5, 0.5
	
	# Loop through physical satellites and generate visualization strings
	for i in data['physical_list']:
		data['physical'][i]["sat_obj"].compute(data['epoch_str'])
		viz_string += "viewer.entities.add({name : '', position: Cesium.Cartesian3.fromDegrees(" \
			+ str(math.degrees(data['physical'][i]["sat_obj"].sublong)) + ", " \
			+ str(math.degrees(data['physical'][i]["sat_obj"].sublat)) + ", "\
			+ str(data['physical'][i]["sat_obj"].elevation) + "), "\
			+ 'billboard :{scale:1.5,\nimage:"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAADJSURBVDhPnZHRDcMgEEMZjVEYpaNklIzSEfLfD4qNnXAJSFWfhO7w2Zc0Tf9QG2rXrEzSUeZLOGm47WoH95x3Hl3jEgilvDgsOQUTqsNl68ezEwn1vae6lceSEEYvvWNT/Rxc4CXQNGadho1NXoJ+9iaqc2xi2xbt23PJCDIB6TQjOC6Bho/sDy3fBQT8PrVhibU7yBFcEPaRxOoeTwbwByCOYf9VGp1BYI1BA+EeHhmfzKbBoJEQwn1yzUZtyspIQUha85MpkNIXB7GizqDEECsAAAAASUVORK5CYII=",}, '\
			+ '});\n'


		# Visualize assignment between virtual and physical satellites	
		for j in data['virtual_list']:
			if assignment[j, i].solution_value() > 0:
				cur_virt_sat = data['virtual'][j]
				color = COLOR_LIST[cur_virt_sat['cid']]

				viz_string += "viewer.entities.add({name : '', position: Cesium.Cartesian3.fromDegrees(" \
					+ str(math.degrees(data['physical'][i]["sat_obj"].sublong)) + ", " \
					+ str(math.degrees(data['physical'][i]["sat_obj"].sublat) + MARKER_POS[cur_virt_sat['cid']]) + ", "\
					+ str(data['physical'][i]["sat_obj"].elevation + MARKER_ELEVATION) + "), "\
					+ "ellipsoid : {radii : new Cesium.Cartesian3("\
					+ str(MARKER_RADIUS) + ", " + str(MARKER_RADIUS) + ", " + str(MARKER_RADIUS) + "), "
				viz_string += "material : Cesium.Color." + color + ".withAlpha(1),}});\n"
	return viz_string

# Solves the satellite assignment problem by assigning virtual satellites to physical satellites
# based on a set of constraints and an optimization objective.
def solve_sat_wrapper(data, virtual_tles, physical_tles):
	'''
	Solves the satellite assignment problem by assigning virtual satellites to physical satellites
	based on a set of constraints and an optimization objective.
	
	Args:
		data (dict): Contains information about the virtual and physical satellites, including their configurations 
			     and any necessary preprocessed data (like position, constraints, etc.).
		virtual_tles (list): Two-Line Element (TLE) data for virtual satellites, used to generate their orbits.
		physical_tles (list): TLE data for physical satellites, used to generate their orbits.
	
	Returns:
		str: A visualization string that shows the assignment results and satellite orbits in CZML format
		     for use with Cesium.
	'''
	solver = pywraplp.Solver.CreateSolver("SCIP")
	x = satsim_solver.solve_sat_wrapper_helper(data, solver) # x[i, j] = 1 if item i is packed in bin j.
	
	status = solver.Solve()
	satsim_solver.print_solve_wrapper_res(solver, status, x, data)
	viz_string = wrapper_visualize(data, x)


	return viz_string + orbit.orbit_czml(virtual_tles) + orbit.orbit_czml(physical_tles)
