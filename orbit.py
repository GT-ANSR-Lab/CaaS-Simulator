from satellite_czml import satellite_czml

def extract_orbit(tle_line2):
    """
    Extract orbit information (the inclination and the Right Ascension (RAAN) of the 
    Ascending Node) for the 2nd line of a TLE entry. 

    Parameters:
    tle_line2 (str): The 2nd line of a TLE, which contains orbital information.

    Returns:
    tuple: A tuple containing the extracted orbital elements:
        - inclination (float): The inclination of the orbit in degrees. 
        - raan (float): The Right Ascension of the Ascending Node in degrees. 
    """
    return float(tle_line2[8:16].strip()), float(tle_line2[17:25].strip())


def tle_file_parser(tle_files):
    """
    Parses TLE files to extract satellite data.

    This function reads a file containing multiple satellites' Two-Line Element (TLE)
    sets, where each set consists of a satellite name followed by two lines of orbital 
    element data. It returns a structured representation of the satellite information.

    Parameters:
    tle_file (str): The file path of the TLE file to be parsed.

    Returns:
    list of list: A list where each element corresponds to a satellite.
    """
    satellites = []
    orbits = set()

    for tle_file in tle_files:
        with open(tle_file, 'r') as f:
            for title_line in f:
                title_line = title_line.strip()
                line_1 = f.readline()
                line_2 = f.readline()
                cur_orbit = extract_orbit(line_2)
                
                if len(orbits) == 0:
                    satellites.append([title_line, line_1, line_2])
                    orbits.add(cur_orbit)
                elif cur_orbit not in orbits:  # remove overlapping orbits
                    for orbit in orbits:
                       if (abs(cur_orbit[0] - orbit[0]) < 1
                            and abs(cur_orbit[1] - orbit[1]) < 1):
                            break
                    else:
                        satellites.append([title_line, line_1, line_2])
                        orbits.add(cur_orbit)
    print('num orbits:', len(satellites))
                                
    return satellites


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