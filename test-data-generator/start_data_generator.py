import sys
import time
import schedule
from src import user_arguments
from src.common import constants
from src.common.fileutils import FileUtil
from src.common.logger import get_logger
from src.common.mqtt_plugin import MqttPlugin

log = get_logger()
file_util = FileUtil()

all_device_data = file_util.parse_json_file(constants.DEVICE_DATA_FILE)
env_data = file_util.parse_json_file(constants.ENVIRONMENT_DATA_FILE)
route_data = file_util.read_file_as_string(constants.ROUTE_DATA_FILE).replace("\"", "")

def start_data_generator(geo_data, duration, vin, proxy_address, proxy_port, args):
    
    def exit_data_gen():
        mqtt_plugin.stop_device()
        sys.exit()
    
    mqtt_plugin = MqttPlugin(device_id)
    start_success = mqtt_plugin.run_device(all_device_data[device_id],env_data, vin = vin, proxy_address=proxy_address, proxy_port=proxy_port, csv_path=args.measurement_data)
    if not start_success:
        exit_data_gen()

    log.info(f"Test Data generator will publish measurement data every {args.playback_speed} seconds and geo position data every {constants.GPS_SAMPLE_SEC} seconds")
    mqtt_plugin.send_messages("VIN",vin = vin)
    mqtt_plugin.send_messages("INVENTORY")
    mqtt_plugin.send_messages("CERTIFICATE_REPORT")

    schedule.every(args.playback_speed).seconds.do(mqtt_plugin.send_messages,"MEASUREMENT",geo_data=geo_data, duration = duration, rm_duration = args.rm_duration)
    schedule.every(constants.GPS_SAMPLE_SEC).seconds.do(mqtt_plugin.send_messages,"GPS", geo_data=geo_data)
    schedule.every(constants.OTA_STATUS_PUBLISH_TIME_SEC).seconds.do(mqtt_plugin.send_messages,"OTA_UPDATE")
    if args.auto_shutdown != -1:
        schedule.every(args.auto_shutdown).minutes.do(exit_data_gen)
    
    try:
        while True:
            if(mqtt_plugin.device_running):
                schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        exit_data_gen()


if __name__ == '__main__':
    try:
        list_of_devices = all_device_data.keys()
        arguments = user_arguments.UserArguments(list_of_devices, route_data)
        arguments.verify_args()
        arguments.args.device
        device_id = arguments.args.device
        route = arguments.args.route
        log.info(f"Device ID: {device_id}")
        device_details = all_device_data[device_id]
        vin = all_device_data[device_id]["vin"]
        geo_data, duration, proxy_address, proxy_port, vin = arguments.get_arg_specific_data(vin)
       
    except KeyError as e:
        log.error(f"Unable to fetch device details for {device_id}, please check if device are available in device_data.json")
        sys.exit()
    
    except (ValueError, ZeroDivisionError) as e:
        log.error("Unable to start Data generator with provided combination of data, Please retry with valid data")
        log.error(e)
        sys.exit()

    start_data_generator(geo_data, duration, vin, proxy_address, proxy_port, arguments.args)