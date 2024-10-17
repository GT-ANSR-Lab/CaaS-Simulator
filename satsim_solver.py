from ortools.linear_solver import pywraplp

try:
	from . import wrapper_calculation
except (ImportError, SystemError):
	import wrapper_calculation

RADIUS = 10000000

def solve_sat_wrapper_helper(data_model, solver):
	"""
	Helper function to solve the satellite assignment problem using Google OR-Tools.

	Parameters:
	    data_model (dict): A dictionary containing the necessary data for the model, including:
	                       - 'virtual_list': List of virtual satellites.
	                       - 'physical_list': List of physical satellites.
	                       - 'virtual': Details of virtual satellites demand.
	                       - 'physical': Details of physical satellites capabilities.
	                       - 'epoch_str': Time epoch for the satellite positions.
	    solver: An instance of a solver from OR-Tools used for optimization.

	    Returns:
	    The dictionary of decision variables containing assignment results and optimization status. 
	"""
	data = data_model
	x = {}
	for i in data["virtual_list"]:
		for j in data["physical_list"]:
			x[(i, j)] = solver.IntVar(0, 1, "x_%i_%i" % (i, j))

	# Constraints
	# Each virtual satellite must be assigned to exactly one physical satellite.
	for i in data["virtual_list"]:
		solver.Add(sum(x[i, j] for j in data["physical_list"]) == 1)

	# Ensures that the demand does not exceed physical satellites capabilities.
	for i in data["physical_list"]:
		physical_obj = data["physical"][i]['sat_obj']
		physical_vars = vars(physical_obj)
		
		for field in physical_vars: 
			# Loop over every var to make sure demand is under physical constraint
			field_value = getattr(physical_obj, field)
			if isinstance(field_value, bool):
				# If the field is a boolean, enforce constraints based on its value.
				for j in data["virtual_list"]:
					solver.Add
					(
						(getattr(data["virtual"][j]['sat_obj'], field) == field_value)
						or (field_value and not getattr(data["virtual"][j]['sat_obj'], field))
					)

			if isinstance(field_value, int) or isinstance(field_value, float):
				# For numerical fields, ensure that the total assigned demand does not exceed capacity.
				solver.Add
				(
					sum(x[j, i] * getattr(data["virtual"][j]['sat_obj'], field)
						for j in data["virtual_list"]) <= field_value
				)

	# Objective: Maximize the total preference score for the assignments.
	solver.Maximize(
		solver.Sum(
			x[i, j] *
			wrapper_calculation.eval_preference(data['virtual'][i]['sat_obj'].ephem_sat,
						   data['physical'][j]['sat_obj'].ephem_sat, RADIUS, data['epoch_str'])
			for i in data['virtual_list'] for j in data['physical_list']))
	return x


def print_solve_wrapper_res(solver, status, assignment, data_model):
	"""
    Prints the results of the satellite assignment optimization.

    Parameters:
    solver: The solver instance used for optimization.
    status: The status of the solver after optimization.
    assignment: The dictionary of decision variables containing assignment results.
    data_model: The data model used in the solver, providing details about the satellites.

    Returns:
    None
    """
	x = assignment
	data = data_model
	print("Solution found:", status == pywraplp.Solver.OPTIMAL)

	if status == pywraplp.Solver.OPTIMAL:
		num_bins = 0
		pref_sum = 0
		for j in data["physical_list"]:
			virt_sats = []
			for i in data["virtual_list"]:
				if x[i, j].solution_value() > 0:
					virt_sats.append(i)
					pref_sum += wrapper_calculation.eval_preference(
						data['virtual'][i]['sat_obj'].ephem_sat,
						data['physical'][j]['sat_obj'].ephem_sat, RADIUS, data['epoch_str']
					)
					# bin_weight += data["virtual"][i]
			if virt_sats:
				num_bins += 1
				print("Phy number", j)
				print("  Virt packed:", virt_sats)
				# print("  Total weight:", bin_weight)
				print()
		print()
		print("Number of phys used:", num_bins)
		print("Preference sum achieved:", pref_sum)
		print("Time = ", solver.WallTime(), " milliseconds")
	else:
		print("The problem does not have an optimal solution.")
