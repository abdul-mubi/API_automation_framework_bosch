from src.common.fileutils import FileUtil
from src.common import constants
from src.common.logger import get_logger
log = get_logger()
file_util = FileUtil()

class DMOperation:
    
    def __init__(self, csv_path):
        self.geo_csv_path = csv_path
        self.geo_data = file_util.read_csv(self.geo_csv_path)
        self.repeat_geo_data = True
    
    def get_geo_details_for_signal(self, signal_name, row_num: int, type = float):
        """Returns geo position data for the signal

        Args:
            signal_name (String): Name of the gps signal
            row_num (int): Sequence counter
            type (_type_, optional): Type of the return value. Defaults to float.

        Raises:
            ValueError:Incase GPS data is not available

        Returns:
            value: Returns GPS Value for the signal
        """
        try:
            if(self.repeat_geo_data == True):
                row = row_num % len(self.geo_data[signal_name].dropna())
            elif row_num >= len(self.geo_data[signal_name]):
                row = len(self.geo_data[signal_name]) - 1
            else:
                row = row_num
            value =  self.geo_data[signal_name][row]
            return type(value)
        except KeyError as e:
            log.error(f"{e} details are not found in {self.geo_csv_path} please update signal/message data")
            raise ValueError(f"GEO Position details : {signal_name} are not available. skipping the position reporting")

    def update_geo_data(self, geo_data):
        """
        Sets the vehicle gps data as per user input
        Args:
            geo_data (dataArray): Geo data generated via geo_calculator
        """
        self.geo_data = geo_data
        self.repeat_geo_data = False