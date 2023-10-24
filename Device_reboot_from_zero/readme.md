# Factory reset
The Factory reset application can be used to reset any TCU1 devices if that device stuck in any in-appropriate state.

## Preconditions
1. Python v3.10 +
2. Install required libraries which are available in requirements.txt file

## Getting Started
Command to start factory reset application -> python start_factory_reset.py --device CCU_2740003527 --hostname 192.168.1.40 --to_version 6.3.1 --factory_reset True

### Command line Arguments:
| Argument          | Usage                                            | Example        | Default Value |
| ----------------- | -------------------------------------------------| ---------------| --------------|
|--device	        |Device id on which factory reset need to be done  | CCU_2740003527 | None          |
|--hostname	        |Hostname of the device                            | 192.168.1.40   | None          |
|--to_version	    |FW Version which is planned to flash on the device| 6.3.1          | None          |
|--factory_reset    |True- factory reset activated                     | True           | False         |
                    |False- only performing base clean up 
### Stage definitions:
Factory reset application has multiple steps to complete perform a succesfull reset. Find the detailed explanation about each stage and its methods.

PREREQUISITES:
    1. delete_auto_created_folder() - Delete auto created folder if there is any
    2. get_device_vin() - Store device vin in global var, will be used to implant same vin after factory reset
    3. check_device_status() - Check device status before performing reset.
    4. get_file_from_artifactory() - Download and store the given FW image and full update package from artifactory and store it in local machine
    5. backup_certificate_from_device() - Copy the device certificate from device and store in local machine before performing reset.

BASIC RESET :
    1. perform_usb_update() - Perform USB update with deleting data partition for the given device FW version
    
FACTORY RESET (If True) :
    1. copy_full_update_to_device() - Move the downloaded full update package to device
    2. install_platform_fw() - Unzip and install platform FW on one partition of the device
    3. check_device_stability(5) - After successfull platform installation, check for the device stability
    4. execute_full_update() - Install full update package on another partition of the device

POSTREQUISITES:
    1. upload_device_certificate() - Move device certificate back to the device
    2. validate_device_version() - Check device has expected FW version
    3. implant_device_vin() - Implant same VIN which was stored in pre-requisites
    4. delete_auto_created_folder() - Delete auto created folder

