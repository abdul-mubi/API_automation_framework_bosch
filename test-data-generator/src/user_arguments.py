import argparse
from src.common import constants
from src.common.logger import get_logger
from src.common.fileutils import FileUtil
from src.common.geo_calculator import GeoCalculator

log = get_logger()
file_util = FileUtil()
geo_calculator = GeoCalculator()


class UserArguments:
    def __init__(self, device_list, route_data):
        parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,add_help=False)
        
        parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='Test Data generator Help')
        
        required_args = parser.add_argument_group('Required Arguments')
        required_args.add_argument("-d", "--device",help='ID of the Device \n Eg: E2E_OTA_DEVICE_001',type=str,choices=device_list, required=True)
        
        gps_args = parser.add_argument_group('Optional GPS Trip simulation arguments')
        gps_args.add_argument("-r", "--route",help=f'Available Routes are: \n {route_data} \n Choose the route ID or city pairs separated by comma \n Eg: Route1 or Stuttgart,Frankfurt ',type=str, required=False)
        gps_args.add_argument("-s", "--speed",help='Speed of Vehicle in Km/Hr \n Eg: 80 or 120',type=int, default= 80, required=False)
        gps_args.add_argument("-v", "--variance",help='Variance in the speed of vehicle in Km/Hr \n Eg: 5 or 10',type=int, default= 5, required=False)
        
        config_args = parser.add_argument_group('Optional configuration arguments')
        config_args.add_argument("--version",action='version', version=constants.VERSION)
        config_args.add_argument("--bfb-support", action='version', version=str(constants.BFB_SUPPORT))
        config_args.add_argument("--log-level",help='Log level for console',type=str,choices=["INFO", "DEBUG","ERROR","WARNING"])
        config_args.add_argument("--proxy", "-p", help='Proxy server to the MQTT connection',type=str, required=False)  
        config_args.add_argument("--auto-shutdown", help='Auto shutdown time in minutes',type=int, default= -1, required=False) 
        config_args.add_argument("--measurement-data", help='Path to measurement CSV file',type=str, default = constants.MEASUREMENT_CSV_PATH, required=False)
        config_args.add_argument("--playback-speed", help='Speed at which test step should be uploaded to backend in seconds',type=int, default= constants.PERIODIC_RM_PUBLISH_TIME_SEC, required=False)
        config_args.add_argument("--rm-duration", help='Duration of the Test step in seconds',type=int, default= constants.MEASUREMENT_RESULT_DURATION_SEC, required=False)
        config_args.add_argument("--vin",help='VIN of vehicle',type=str, required=False)
        self.args = parser.parse_args()
        
    
    def verify_args(self):
        """Verifies the Arguments passed by the user via CLI

        Raises:
            ValueError: If the measurement File is invalid / Playback speed is invalid / Measurement duration is invalid
        """
        if self.args.auto_shutdown > 0 :
            log.info(f"Setting Auto shutdown time for {self.args.auto_shutdown} minutes")

        if self.args.measurement_data:
            if not file_util.check_file_availability(self.args.measurement_data):
                log.error(f"Selected measurement data file {self.args.measurement_data} is not available, Please recheck the path or availability of the file")
                raise ValueError("Invalid Measurement data file")
            else:
                log.debug(f"Choosing measurement input file as {self.args.measurement_data}")
                file_util.read_csv(self.args.measurement_data)

        if self.args.playback_speed < 1:
            log.error(f"Invalid playback speed {self.args.playback_speed} please choose a value, which is greater than 0")
            raise ValueError("Invalid playback speed value")
        log.info(f"Playback speed is {self.args.playback_speed} seconds. Each measurement upload cycle will be uploaded every {self.args.playback_speed} seconds")

        if self.args.rm_duration < 1:
            log.error(f"Invalid measurement duration.{self.args.rm_duration} please choose a value, which is greater than 0")
            raise ValueError("Invalid Measurement duration")
        log.info(f"Measurement test step duration is {self.args.rm_duration} seconds")
        
    
    def get_arg_specific_data(self, vin):
        """Based on the user argument input, the required data for GPS trip, VIN, Proxy will be fetched and returned

        Args:
            vin (str): Default VIN of the Vehicle

        Returns:
            geo_data (Pandas.DataArray): If user selects a GPS trip, simulated values of the GPS trip will be returned
            duration (int): Duration of the Trip in seconds
            proxy_address(str): Proxy address
            proxy_port(int): Proxy Port
            vin(str): VIN of the vehicle
        """

        geo_data, duration, proxy_address, proxy_port = None, None, None, None
        
        if self.args.log_level:
            log.info(f"Updating log level to {self.args.log_level}")
            log.setLevel(self.args.log_level)
        
        if self.args.proxy:
            proxy_data= self.args.proxy.split(":")
            proxy_address = proxy_data[0]
            if(len(proxy_data)>1):
                proxy_port = int(proxy_data[1])
            else:
                log.debug("Choosing default proxy port for proxy")
                proxy_port = 8080
            log.debug(f"Selected proxy address: {proxy_address} and port: {proxy_port}")
        
        if self.args.vin:
            if(self.args.vin).isalnum() and len(self.args.vin) == 17:
                log.info(f"Selected vin for vehicle is {self.args.vin}")
                vin = self.args.vin
            else:
                log.error("Invalid VIN. Entered VIN is not 17 digit Alpha numeric value")
                log.info(f"Proceeding with default VIN: {vin}")

        if(self.args.route != None):
                geo_data, duration = geo_calculator.generate_geo_data(self.args.route,self.args.speed, self.args.variance)
        
        return geo_data, duration, proxy_address, proxy_port, vin