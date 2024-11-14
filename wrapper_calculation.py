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
