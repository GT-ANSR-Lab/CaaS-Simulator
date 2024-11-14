import ephem
import math
from datetime import datetime
import pytz
import json
from geopy.distance import great_circle
from astropy.time import Time
from astropy import units as u
from ortools.linear_solver import pywraplp
import random
try:
	from . import satellite
	from . import util
	from . import orbit
	from . import satsim_solver
except (ImportError, SystemError):
	import satellite
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


def generate_sat_obj_list(
		num_orbit,
		num_sats_per_orbit,
		epoch,
		phase_diff,
		inclination,
		eccentricity,
		arg_perigee,
		mean_motion
):
	
	'''
	Generates list of satellite objects based on orbital parameters. 
	
	Returns:
		List: List of satellite objects
 	'''
	
	sat_objs = [None] * (num_orbit * num_sats_per_orbit)
	counter = 0
	for orb in range(0, num_orbit):
		raan = orb * 360 / num_orbit
		orbit_wise_shift = 0
		if orb % 2 == 1:
			if phase_diff:
				orbit_wise_shift = 360 / (num_sats_per_orbit * 2)

		for n_sat in range(0, num_sats_per_orbit):
			mean_anomaly = orbit_wise_shift + (n_sat * 360 / num_sats_per_orbit)

			sat = ephem.EarthSatellite()
			sat._epoch = epoch
			sat._inc = ephem.degrees(inclination)
			sat._e = eccentricity
			sat._raan = ephem.degrees(raan)
			sat._ap = arg_perigee
			sat._M = ephem.degrees(mean_anomaly)
			sat._n = mean_motion

			sat_objs[counter] = {
				"sat_obj": sat, #make custom sat
			}
			counter += 1
	return sat_objs


def generate_sat_obj_wrapper_list(
	num_orbit,
	num_sats_per_orbit,
	epoch,
	phase_diff,
	inclination,
	eccentricity,
	arg_perigee,
	mean_motion
):
	"""
	Generates list of satellite objects based on orbital parameters. 
	
	Returns:
		List: List of satellite objects
	"""
	sat_objs = [None] * (num_orbit * num_sats_per_orbit)
	counter = 0
	for orb in range(0, num_orbit):
		raan = orb * 360 / num_orbit
		orbit_wise_shift = 0
		if orb % 2 == 1:
			if phase_diff:
				orbit_wise_shift = 360 / (num_sats_per_orbit * 2)
	
		for n_sat in range(0, num_sats_per_orbit):
			mean_anomaly = orbit_wise_shift + (n_sat * 360 / num_sats_per_orbit)
	
			sat = ephem.EarthSatellite()
			sat._epoch = epoch
			sat._inc = ephem.degrees(inclination)
			sat._e = eccentricity
			sat._raan = ephem.degrees(raan)
			sat._ap = arg_perigee
			sat._M = ephem.degrees(mean_anomaly)
			sat._n = mean_motion
			
			sat_wrapper = satellite.Satellite(sat)
			
			sat_objs[counter] = {
				"sat_obj": sat_wrapper,
			}
			counter += 1
	return sat_objs

#README
def write_viz_files(viz_string, top_file, bottom_file, out_file):
	"""
	Writes a visualization HTML string to a HTML file by combining content from the top, bottom, and a generated visualization string.
	
	Args:
		viz_string (str): The string containing the visualization content.
		top_file (str): Filepath to the top part of the HTML template.
		bottom_file (str): Filepath to the bottom part of the HTML template.
		out_file (str): Output file to write the final combined content.
	
	Returns:
		None
	"""
	writer_html = open(out_file, 'w')
	with open(top_file, 'r') as fi:
		writer_html.write(fi.read())
	writer_html.write(viz_string)
	with open(bottom_file, 'r') as fb:
		writer_html.write(fb.read())
	writer_html.close()


def distance_m_between_satellites(sat1, sat2, epoch_str, date_str):
	"""
	Calculates the distance two satellites at a specific epoch and date.
	
	Args:
		sat1 (ephem.EarthSatellite): The first satellite object.
		sat2 (ephem.EarthSatellite): The second satellite object.
		epoch_str (str): The epoch time string (in TLE format).
		date_str (str): The observation date string (in ephem date format).
	
	Returns:
		float: The distance between the two satellites.
	"""
	# Create an observer on the planet
	observer = ephem.Observer()
	observer.epoch = epoch_str
	observer.date = date_str
	observer.lat = 0
	observer.lon = 0
	observer.elevation = 0

	# Calculate the relative location of the satellites to this observer
	sat1.compute(observer)
	sat2.compute(observer)

	# Calculate the angle observed by the observer to the satellites (this is done because the .compute() calls earlier)
	angle_radians = float(repr(ephem.separation(sat1, sat2)))

	return math.sqrt(sat1.range ** 2 + sat2.range ** 2 - (2 * sat1.range * sat2.range * math.cos(angle_radians)))


def read_tles(filename_tles):
	"""
	Reads a TLE file and extracts satellite information.
	
	Args:
		filename_tles (str): Path to the file containing TLE data.
	
	Returns:
		List[dict]: A list of dictionaries, each satellite object the satellite's name.
	"""
	satellites = []
	with open(filename_tles, 'r') as f:

		for tles_line_1 in f:
			tles_line_2 = f.readline()
			tles_line_3 = f.readline()

			# Retrieve name and identifier
			name = tles_line_1
			epoch_year = tles_line_2[18:20]
			epoch_day = float(tles_line_2[20:32])
			epoch = Time("20" + epoch_year + "-01-01 00:00:00", scale="tdb") + (epoch_day - 1) * u.day


			# Store the satellite information
			satellites.append({
				'sat_obj':ephem.readtle(tles_line_1, tles_line_2, tles_line_3), 
				'name' : name
				})
	return satellites

def read_json(json_filenames):
	"""
	Reads satellite configuration data from JSON files.
	
	Args:
		json_filenames (List[str]): List of JSON file paths.
	
	Returns:
		List[dict]: A list of satellite configurations.
	"""
	sat_config = []
	for json_path in json_filenames:
		with open(json_path, "r") as file:
			json_data = file.read()
			sat_config.extend(json.loads(json_data))
	return sat_config

def sat_setup(sat_dict, cur_sat):
	cur_sat.name = sat_dict['name'] #str
	cur_sat.rgb = sat_dict['rgb'] #bool
	cur_sat.hyperspectral = sat_dict['hyperspectral'] # bool
	cur_sat.radar = sat_dict['radar'] # bool
	cur_sat.CPU = sat_dict['CPU'] # int
	cur_sat.memory = sat_dict['memory'] # int
	cur_sat.storage = sat_dict['storage'] #int
	cur_sat.GPU = sat_dict['GPU'] #bool
	cur_sat.FPGA = sat_dict['FPGA'] #bool
	cur_sat.ISL_capcity = sat_dict['ISL_capcity'] #int
	cur_sat.GSL_capacity = sat_dict['GSL_capacity'] #int
	cur_sat.range = sat_dict['range'] #int


def const_setup(tles_files):
	"""
	Sets up the satellite constellation based on TLE (Two-Line Element) files.
	
	Parameters:
	tles_files (list): A list of file paths to TLE files, each TLE file represent a constellation. 
	
	Returns:
	tuple: A tuple containing a list of dictionary of satellite objects, name, and constellation ID,  and the number of constellations.
	"""
	satellites = []
	cid = 0
	for each in tles_files:
		with open(each, 'r') as f:
			for tles_line_1 in f:
				tles_line_2 = f.readline()
				tles_line_3 = f.readline()
				
				name = tles_line_1.strip()
				cur_ephem_sat = ephem.readtle(tles_line_1, tles_line_2, tles_line_3)
				cur_sat = satellite.Satellite(cur_ephem_sat)

				satellites.append({
					'sat_obj':cur_sat, 
					'name' : name,
					'cid' : cid
				})
		cid += 1
	return satellites, cid


def const_setup_per_sat_config(tles_file, json_file):
	"""
	Sets up a satellite constellation based on TLE and per-satellite configuration files.
	
	Parameters:
	tles_file (list): A list of TLE file paths, each TLE file represent a constellation. 
	json_file (str): Path to the JSON file containing per-satellite configuration.
	
	Returns:
	tuple: A tuple containing a list of dictionary of satellite objects, name, and constellation ID,  and the number of constellations.
	"""
	satellites = []
	cid = 0
	sat_config = read_json(json_file)
	i = 0
	for each in tles_file:
		with open(each, 'r') as f:
			for tles_line_1 in f:
				tles_line_2 = f.readline()
				tles_line_3 = f.readline()

				name = tles_line_1.strip()
				cur_ephem_sat = ephem.readtle(tles_line_1, tles_line_2, tles_line_3)
				cur_sat = satellite.Satellite(cur_ephem_sat)
				sat_setup(sat_config[i], cur_sat)

				satellites.append({
					'sat_obj':cur_sat, 
					'name' : name,
					'cid' : cid
				})
			i +=1
		cid += 1
	return satellites, cid


def const_setup_universal_config(tles_file, json_file):
	"""
	Sets up a satellite constellation based on TLE files and a universal satellite configuration.
	
	Parameters:
	tles_file (list): A list of TLE file paths, each TLE file represent a constellation. 
	json_file (str): A list of JSON file paths containing universal satellite configurations.
	
	Returns:
	tuple: A tuple containing a list of dictionary of satellite objects, name, and constellation ID,  and the number of constellations.
	"""
	satellites = []
	cid = 0
	with open(json_file[cid], 'r') as file:
		sat_config = json.load(file)
	for each in tles_file:
		with open(each, 'r') as f:
			for tles_line_1 in f:
				tles_line_2 = f.readline()
				tles_line_3 = f.readline()

				name = tles_line_1.strip()
				cur_ephem_sat = ephem.readtle(tles_line_1, tles_line_2, tles_line_3)
				cur_sat = satellite.Satellite(cur_ephem_sat)
				sat_setup(sat_config, cur_sat)
				print(cur_sat.name)

				satellites.append({
					'sat_obj':cur_sat, 
					'name' : name,
					'cid' : cid
				})
		cid += 1

	return satellites, cid


def satellite_ephem_to_str(satellite_ephem):
	"""
	Converts a satellite ephem object to its string representation.
	
	Parameters:
	satellite_ephem (object): A satellite ephem object containing various satellite properties.
	
	Returns:
	str: A formatted string representation of the satellite's ephem data.
	"""
	res = "EphemSatellite {\n"
	res += "  name = \"" + str(satellite_ephem.name) + "\",\n"
	res += "  _ap = " + str(satellite_ephem._ap) + ",\n"
	res += "  _decay = " + str(satellite_ephem._decay) + ",\n"
	res += "  _drag = " + str(satellite_ephem._drag) + ",\n"
	res += "  _e = " + str(satellite_ephem._e) + ",\n"
	res += "  _epoch = " + str(satellite_ephem._epoch) + ",\n"
	res += "  _inc = " + str(satellite_ephem._inc) + ",\n"
	res += "  _M = " + str(satellite_ephem._M) + ",\n"
	res += "  _n = " + str(satellite_ephem._n) + ",\n"
	res += "  _orbit = " + str(satellite_ephem._orbit) + ",\n"
	res += "  _raan = " + str(satellite_ephem._raan) + "\n"
	res += "}"
	return res


def generate_100_coordinates_around_europe():
	'''
	latitudes 34° North and 81° North, 
	longitudes 31° West and 69° East
	'''
	coordinates = []
	for _ in range(100):
		coordinate = (random.uniform(34, 81), random.uniform(31, 69))
		coordinates.append(coordinate)
	return coordinates

#FIX README
# Create data with tles information about the virtual and physical constellations
def create_data(virtual_tles, physical_tles):
	data = {}
	start_time = datetime.utcnow().replace(tzinfo=pytz.UTC) + timedelta(hours=1)
	data['epoch_str'] = start_time.strftime("%Y-%m-%d %H:%M:%S")

	data["virtual"], data["num_virtual_const"] = const_setup(virtual_tles)
	data["physical"], num_phys_const = const_setup(physical_tles)

	data["virtual_list"] = list(range(len(data["virtual"])))
	data["physical_list"] = list(range(len(data['physical'])))

	return data


# Create data with tles information about the virtual and physical constellations, 
# but uses universal config files for constellation setup
def create_data_universal(virtual_tles, physical_tles, physical_json_file, virtual_json_files):
	data = {}
	start_time = datetime.utcnow().replace(tzinfo=pytz.UTC) + timedelta(hours=1)
	data['epoch_str'] = start_time.strftime("%Y-%m-%d %H:%M:%S")

	data["virtual"], data["num_virtual_const"] = const_setup_universal_config(virtual_tles, virtual_json_files)
	data["physical"], num_phys_const = const_setup_universal_config(physical_tles, physical_json_file)

	data["virtual_list"] = list(range(len(data["virtual"])))
	data["physical_list"] = list(range(len(data['physical'])))

	return data

# Create data per satellite (with individual config files for each satellite constellation)
def create_data_per_sat(virtual_tles, physical_tles, virtual_json_file, physical_json_file):
	data = {}
	start_time = datetime.utcnow().replace(tzinfo=pytz.UTC) + timedelta(hours=1)
	data['epoch_str'] = start_time.strftime("%Y-%m-%d %H:%M:%S")

	data["virtual"], data["num_virtual_const"] = const_setup_per_sat_config(virtual_tles, virtual_json_file)
	data["physical"], num_phys_const = const_setup_per_sat_config(physical_tles, physical_json_file)

	data["virtual_list"] = list(range(len(data["virtual"])))
	data["physical_list"] = list(range(len(data['physical'])))

	return data


# Evaluate the preference of a virtual satellite to connect with a physical satellite based on distance
def eval_preference(virtual_sat, phys_sat, radius, epoch):
	distance = distance_m_between_satellites(virtual_sat, phys_sat, epoch, epoch)
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


def orbit_czml(tle_file):
    """
    Generates a CZML string for visualizing satellite orbits.

    Parameters:
    tle_file (list): A list of file paths containing TLE data.

    Returns:
    str: A JavaScript string that initializes the CZML data for use with CesiumJS to
         visualize the satellite orbits on a 3D globe.
    """

    single_tle = tle_file_parser(tle_file)

    czml_string = satellite_czml(tle_list=single_tle).get_czml()
    return "\nvar czml_data =" + czml_string + ";\nviewer.dataSources.add(Cesium.CzmlDataSource.load(czml_data));\n"