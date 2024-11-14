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