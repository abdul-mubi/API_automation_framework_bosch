# Test Data Generator


## Preconditions
1. Python v3.x
2. Internet Access to the MQTT URLS (Proxy/ BTIA/ Whitelisting)
3. Device key,certificate in .pem format
## Dependencies

Dependencies are defined in:
- `requirements.txt`

## First steps

1. Install the necessary dependencies execute
```
pip install -r requirements.txt --proxy=https://rb-proxy-in.bosch.com:8080
```

2. Provide Environment details and proxy related details (if applicable) in the **'userdata/environment.json'** file
3. Copy the device certificates to **'userdata/certificates/'** directory
4. Mention the path to the '*.pem' certificates in the 'device_data.json' file along with environment of the device

## Usage

To run the Application, first navigate to test-data-generator root directory via terminal and type following command:
```
python .\start_data_generator.py -d <DEVICE_ID>
```
or 
```
python .\start_data_generator.py --device <DEVICE_ID>
```

Additional parameters can be used to run the data generator with GPS simulation based on city pairs

```
python .\start_data_generator.py --device <DEVICE_ID> --route <RouteID or city pairs separated by comma> --speed <Speed of vehicle in Km/h> --variance <Variance of the speed>

```
Eg:
```
python .\start_data_generator.py --device E2E_OTA_DEVICE_001 --route Route3 --speed 80 --variance 10  
```
Once the required operation is completed, safely close the terminal window.

### Additional Command line Arguments:


| Argument          | Usage                              | Example                   | Default Value                             |
| ----------------- | ---------------------------------- | ------------------------- | ----------------------------------------  |
|--version	        |Display version of the Simulator    | 1.0.0                     |                                           |
|--bfb-support      |Display supported BFB Versions      |otaVehicleData -2          |                                           |
|--log-level        |Set log level                       |DEBUG or ERROR             | INFO                                      |
|--proxy / -p       |Proxy to connect to backend         |rb-proxy-in.bosch.com:8080 | proxy from userdata/environment.json      |
|--auto-shutdown    |Shut down time in minutes           |20                         | -1 (No auto Shutdown)                     |
|--measurement-data |Measurement data csv file           |rm_data.csv                | userdata/measurement/measurement_data.csv |
|--playback-speed   |Measurement upload speed in seconds |10                         | 1 (Each upload cycle for every 1 sec)     |
|--rm-duration      |Measurement step duration in seconds|100                        | 180 (3 minutes)                           |
|--vin              |Vin of the Vehicle                  |AUT20201010123456          | vin from deviceData.json                  |

## Supported BFB Versions: 
1. VehicleData- V2
2. DeviceManagement- V2
3. deviceVehicleMapping - V2
4. softwareUpdate - V2
5. inventory -V3

## Measurement Result Data:
Measurement result data is stored in the **'userdata/measurement/measurement_data.csv'** directory
Currently Data generator supports following Result Data.
1. Double
2. Byte
3. String
4. List of Double
5. GPS Data

By default one test step will be generated for each measurement with 4 upload cycles when Data generator is online.
in case multiple Test steps/additional upload are required,
Following variables should be updated in **'src/common/constants.py'**
1. MEASUREMENT_RESULT_DURATION_SEC - Duration of the individual measurement result
2. CONTINUOUS_REPORTING - True/False : If set as true, A new test step will be generated once the current test step Upload cycle is complete

### Note:
1. Once RM Activation command is received, measurement Job details are stored at **'temp/DEVICE_ID/RM_CONFIGS'**  directory.
2. When RM Deactivation command is received, the measurement job details are automatically deleted from the temp directory.
3. When GPS trip details are provided as part of Data generator, assigned GPS related measurement job should have "GPS or gps" in its name.

## OTA Updates:
Happy path flow is supported for OTA Update. User can send both un-encrypted/ encrypted distribution packages as part of the assignment.
In case inventory needs to be updated once the assignment is completed, update package should be a JSON file which contains inventory change information and type of the distribution package should be BASIC and encryption should be NONE. 
Update Packages (JSON files) are located at: **'userdata/ota_update'** directory

## Inventory:
Inventory is reported to backend at the time of startup. If the device is started for the first time, a default inventory value will be set, which is located at **'userdata/default_inventory.json'**. Once the OTA update is performed, device would send the inventory report again to backend.
Incase the OTA update had inventory changes, that will be reflected as part of new device inventory file and it will be sent to backend.

## Docker container:
As userdata directory contains data specific to the device,environment and playback data, Docker image do not contain userdata folder. While running the container, user can mount the userdata directory via volume mount feature on Docker.

```
docker run -v <Path_to_userdata_dir>:/userdata -e device_data="-d E2E_OTA_DEVICE_001 --route=Route3" <DOCKER_IMAGE_NAME>
```

Note: userdata folder will contains device certificates, environment.json and device_data.json and measurement related files.