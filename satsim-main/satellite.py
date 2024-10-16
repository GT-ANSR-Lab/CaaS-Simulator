import ephem

class Satellite:
	"""
	A class representing a satellite with its orbital parameters and capabilities.

	This class serves as a wrapper around the ephem.EarthSatellite object, and 
	provides attributes to store satellite-specific information and methods to read 
	TLE data and compute orbital positions.
	"""

	def __init__(self, ephem_satellite: ephem.EarthSatellite): 
		if ephem_satellite:
			self.ephem_sat = ephem_satellite
		self.name = ""
		self.rgb = False
		self.hyperspectral = False
		self.radar = False
		self.CPU = 0
		self.memory = 0
		self.storage = 0
		self.GPU = False
		self.FPGA = False
		self.ISL_capcity = 0
		self.GSL_capacity = 0
		self.range = 0


	def readtle(self, tle_title, tle_1, tle_2):
		self.__init__(ephem.readtle(tle_title, tle_1, tle_2))
		return self.ephem_sat


	def compute(self, date_or_observer):
		self.ephem_sat.compute(date_or_observer)

	@property
	def sublong(self):
		return self.ephem_sat.sublong

	@property
	def sublat(self):
		return self.ephem_sat.sublat
	
	@property 
	def elevation(self):
		return self.ephem_sat.elevation
