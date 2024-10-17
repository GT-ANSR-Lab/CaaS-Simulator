import ephem
import math
from datetime import datetime
import pytz
import json
from geopy.distance import great_circle
from astropy.time import Time
from astropy import units as u
import random
try:
	from . import satellite
except (ImportError, SystemError):
	import satellite


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
	sat_config = read_json(json_file) # util.read_json("test.json")
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
