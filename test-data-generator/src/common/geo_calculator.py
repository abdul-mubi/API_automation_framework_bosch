import math
import numpy
import pandas
import random
from src.common.fileutils import FileUtil
from src.common.logger import get_logger
from src.common import constants
log = get_logger()
fileutil = FileUtil()

class GeoCalculator:
    """
    This class is used to generate the GPS related data
    """
        
    def generate_geo_data(self, city_pair, speed_kmph :int, speed_variance: int):
        """
        Generates the gps trip data based on the input parameters
        Args:
            city_pair (String): Route Id or the city names separated by comma
            speed_kmph (int): speed of the vehicle
            speed_variance (int): variance in the speed

        Returns:
            DataArray: DataArray consisting the trip data based on speed
        """
        gps_result = []
        min_distance =  ((speed_kmph - speed_variance) / 3.6) * constants.GPS_SAMPLE_SEC
        max_distance =  ((speed_kmph + speed_variance) / 3.6) * constants.GPS_SAMPLE_SEC
        previous_distance = 0
        trip_distance = 0
        way_points_data = self.get_geo_data_for_city_pair(city_pair)
        self.heading_distance_between_points(way_points_data)
        way_points_data = self.generate_intermediate_geo_points(way_points_data, min_distance)
        for way_point_id in range (len(way_points_data) ):
            longitude = way_points_data[way_point_id][0]
            latitude = way_points_data[way_point_id][1]
            altitude =way_points_data[way_point_id][2]
            heading = way_points_data[way_point_id][3]
            trip_distance += way_points_data[way_point_id][4]
            distance_diff = trip_distance - previous_distance
            if(way_point_id==0 or way_point_id == len(way_points_data)-1 or 
               ((distance_diff) >= min_distance and ((distance_diff) + way_points_data[way_point_id + 1][4] ) >= random.uniform(min_distance, max_distance) )):
                speed = ((trip_distance - previous_distance)/constants.GPS_SAMPLE_SEC)*3.6
                gps_result.append({"GPSLongitude": longitude, 
                                   "GPSLatitude": latitude, 
                                   "GPSHeading": heading, 
                                   "GPSTripDistance": trip_distance,
                                   "GPSSpeed":speed,
                                   "GPSAltitude" : altitude})
                previous_distance = trip_distance
        last_data = gps_result[len(gps_result)-1]
        last_data["GPSSpeed"] = 0
        gps_result.append(last_data)
        total_duration = len(gps_result) * constants.GPS_SAMPLE_SEC
        log.info(f"Total Samples after generating trip {len(gps_result)} and Generated trip distance: {trip_distance} m, duration: {total_duration} s")
        return pandas.DataFrame(gps_result), total_duration
    
    def __get_heading(self, first_waypoint, second_waypoint):
        """
        Generates GPS heading from first way point to second

        Args:
            first_waypoint (List): Waypoint Data, which is part of GeoJson 
                                    (List that contains longitude, latitude and altitude values)
            second_waypoint (List): Waypoint Data, which is part of GeoJson 
                                    (List that contains longitude, latitude and altitude values)

        Returns:
            float: Heading in degrees from first way point to second
        """
        long_diff = second_waypoint[0] - first_waypoint[0]
        x = math.cos(math.radians(second_waypoint[1])) * math.sin(math.radians(long_diff))
        y = math.cos(math.radians(first_waypoint[1])) * math.sin(math.radians(second_waypoint[1])) - math.sin(math.radians(first_waypoint[1])) * math.cos(math.radians(second_waypoint[1])) * math.cos(math.radians(long_diff))
        heading_deg = numpy.degrees(numpy.arctan2(x,y))
        return heading_deg % 360
    
    def __distance_between_two_points(self, first_waypoint, second_waypoint):
        """
        Calculates trip distance between two waypoints and returns the data

        Args:
            first_waypoint (List): Waypoint Data, which is part of GeoJson 
                                    (List that contains longitude, latitude and altitude values)
            second_waypoint (List): Waypoint Data, which is part of GeoJson 
                                    (List that contains longitude, latitude and altitude values)

        Returns:
            float: Distance from first point to second
        """
        R = 6372800
        r_lat_one, r_lat_two = math.radians(first_waypoint[1]), math.radians(second_waypoint[1]) 
        r_lat_diff = math.radians(second_waypoint[1] - first_waypoint[1])
        r_long_diff = math.radians(second_waypoint[0] - first_waypoint[0])
        
        a = math.sin(r_lat_diff/2)**2 + \
            math.cos(r_lat_one)*math.cos(r_lat_two)*math.sin(r_long_diff/2)**2

        return 2*R*math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def get_geo_data_for_city_pair(self,city_data):
        """
        Gets the geo data for the given city pair data
        Args:
            city_data (String):  Route Id or the city names separated by comma

        Raises:
            ValueError: When the city pair data is not valid

        Returns:
            list: Waypoint Data, which is part of GeoJson (List that contains longitude, latitude and altitude values)
        """
        way_points_data = []
        route_data = fileutil.parse_json_file(constants.ROUTE_DATA_FILE)
        city_data = city_data.replace(" ", "")
        if(city_data in route_data):
            city_pair_list = route_data[city_data]
        else:
            city_pair_list = city_data.split(",")
        cities_size = len(city_pair_list)
        if(cities_size<2):
            log.error("Error unable to generate trip data with single city value")
            raise ValueError("Please select more than one city in specified routes or a valid route")
        log.info(f"Geo Data will be generated for {city_pair_list}")
        for count in range(cities_size-1):
            city1 = city_pair_list[count]
            city2 = city_pair_list[count + 1]
            if(fileutil.check_file_availability(f"userdata/geodata/{city1}-{city2}.geojson")):
                geo_data = fileutil.parse_json_file(f"userdata/geodata/{city1}-{city2}.geojson")
                way_points_data.extend(geo_data['features'][0]['geometry']["coordinates"])
            else:
                log.error("City Pair Data is not valid, please select existing city pair data")
                raise ValueError(f"CityPairData {city1}-{city2} is not available")
        return way_points_data
    
    def heading_distance_between_points(self, way_points_data):
        """
        Updates the Heading and distance between two points to the waypoint data list
        Args:
            way_points_data (list): way_points_data 

        Returns:
            list: way_points_data including heading and distance data
        """
        previous_way_pt = 0
        for way_point_id in range (len(way_points_data)):
            way_points_data[way_point_id].append(self.__get_heading(way_points_data[previous_way_pt],way_points_data[way_point_id]))
            way_points_data[way_point_id].append(self.__distance_between_two_points(way_points_data[previous_way_pt],way_points_data[way_point_id]))
            previous_way_pt = way_point_id
        return way_points_data
    
    def generate_intermediate_geo_points(self, way_points_data, min_distance):
        """
        Intermediate geo points will be generated in the existing waypoints data,
        when the min distance is lesser than distance between way_points

        Args:
            way_points_data (list): Waypoints data
            min_distance (int): Min distance between two points

        Returns:
            _type_: _description_
        """
        previous_way_pt = 0
        add_data_counter = 0
        prev_distance = 0
        new_data_list = way_points_data.copy()
        for way_point_id in range (len(way_points_data)):
            if (way_points_data[way_point_id][4] + prev_distance) > (min_distance / 10):
                intermediate_points = math.ceil((way_points_data[way_point_id][4] + prev_distance) / (min_distance / 10))
                counter_pos = way_point_id + add_data_counter
                del new_data_list[counter_pos]
                new_data_list[counter_pos:counter_pos] = self.__prepare_intermediate_points_data(intermediate_points,way_points_data[previous_way_pt], way_points_data[way_point_id])
                add_data_counter += (intermediate_points -1)
                prev_distance = 0
            else:
                prev_distance = way_points_data[way_point_id][4]
            previous_way_pt = way_point_id
            
        return new_data_list
    
    def __prepare_intermediate_points_data(self, intermediate_points, first_way_point, second_way_point):
        """
        Prepares intermediate geo points data based on the input

        Args:
            intermediate_points (int):Number of required intermediate points
            first_way_point (list): Waypoint Data, which is part of GeoJson 
                                    (List that contains longitude, latitude and altitude values)
            second_way_point (list): Waypoint Data, which is part of GeoJson 
                                    (List that contains longitude, latitude and altitude values)

        Returns:
            list: Contains information of the intermediate waypoints
        """
        intermediate_wp = [first_way_point[0:2]]
        long_diff_per_point = (second_way_point[0] - first_way_point[0]) / intermediate_points
        lat_diff_per_point = (second_way_point[1] - first_way_point[1]) / intermediate_points
        elevation_diff_per_point = (second_way_point[2] - first_way_point[2]) / intermediate_points
        for count in range (1, intermediate_points):
            wp_data = []
            wp_data.append(first_way_point[0] + count * long_diff_per_point)
            wp_data.append(first_way_point[1] + count * lat_diff_per_point)
            wp_data.append(first_way_point[2] + count * elevation_diff_per_point)
            intermediate_wp.append(wp_data)
        intermediate_wp.append(second_way_point[0:3])
        self.heading_distance_between_points(intermediate_wp)
        del (intermediate_wp[0])
        return intermediate_wp