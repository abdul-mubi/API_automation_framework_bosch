import requests
import logging
import time
import datetime
import os
import json
import logging
import utils.API_Requests as API_Requests
import pageObjects.API_OTA_Vehicle_Data_Class as API_OTA_Vehicle_Data_Class
import pageObjects.API_Generic_Class as API_Generic_Class
import pageObjects.API_FleetManagement_Class as API_FleetManagement_Class
import steps.constantfiles.constants_ota_vehicle_data as constants
import steps.constantfiles.constants_campaign as constantscampaign

@step('create signal collection "{signal_collection_name}" if it is not available')
@step('create signal collection "{signal_collection_name}" using "{signal_data}" if it is not available')
def step_impl(context, signal_collection_name, signal_data=None):
    """ Descirption : Check if the signal collection is available or else create it

    Pre-condition : None

    Parameters  : 
        signal_collection : The signal collection which need to be used     
        signal_data : data in formate[key:value]
         Possible keys:  name
                            protocol("CAN_RAW","J1939","XCP_ON_CAN")
                            input("DBC","A2L")
                            version
                            description
                            transmissionRate
                            samplePoit
                            btlCycles
                            sjw
                            fileName
    Examples
        1.  "protocol:CAN_RAW,input:DBC,vesrion:1,description:,transmissionRate:500000,samplePoit:70,btlCycles:10,sjw:2,fileName:MONonCAN_Endurance.dbc"
        2.  "transmissionRate:500000,samplePoit:70,btlCycles:10,sjw:2"
        3.  "transmissionRate:500000"
    Expected result : 
        signal_collection_id :  Id of the singal collection

    Note : Additional step to create a new signal collection needs to be done

    """
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    context.signal_collection_id = api_rm_obj.get_signal_collection_id(signal_collection_name)
    if context.signal_collection_id is None:
        file_name = "MONonCAN_Endurance.dbc"
        pay_load = {
            "name":"",
            "protocol":"CAN_RAW",
            "input":"DBC",
            "version":"1",
            "description":"",
            "transmissionRate":"500000",
            "samplePoit":"70",
            "btlCycles":"10",
            "sjw":"2"
        }

        if signal_data != " ":
            test_data = signal_data.split(',')
            for data in test_data:
                if data.split(':')[0] in pay_load:
                    pay_load[data.split(':')[0]] = data.split(':')[1]
                elif 'fileName' in data.split(':')[0]:
                    file_name = data.split(':')[1]

        pay_load['name'] = signal_collection_name
        api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details) 
        file_path = os.getcwd() + constants.OTA_VEHICLE_DATA + pay_load['protocol']+'\\' + file_name
        logging.info(file_path)
        files = {'file': open(file_path, 'rb')}
        r = api_rm_obj.create_signal_collection(constants.RM_SIG_COL,pay_load,files)
        assert r.status_code == requests.codes.created,"Collection creation error"
    else:
        logging.info(f'Signal collection  {signal_collection_name} is already present')
    time.sleep(5) # time to create Signal creation at the backend
    r = api_rm_obj.get_signal_collection(signal_collection_name)
    logging.info(r)
    assert r.json()['_embedded']['signalCollections'][0]['fileImportState'].lower() == "SUCCESSFUL".lower() or r.json()['_embedded']['signalCollections'][0]['fileImportState'].lower() == "SYSTEM".lower(),"Single collection state is not as expected. Actual state - "+r.json()['_embedded']['signalCollections'][0]['fileImportState']
    context.signal_collection_id = r.json()['_embedded']['signalCollections'][0]['signalCollectionId']
    context.signal_collection_name = r.json()['_embedded']['signalCollections'][0]['name']


@step('release signal collection "{signal_collection_name}"')
def step_impl(context,signal_collection_name):
    """Releases the signal from draft state
    
        Parameter :
            signal_collection_name : "Signal collection name"
    
    
    """
    context.signal_collection_name = signal_collection_name
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)  
    r = api_rm_obj.get_signal_collection(context.signal_collection_name)
    if r.json()['_embedded']['signalCollections'][0]['state'] == "RELEASED":
        logging.info(context.signal_collection_name + 'is already in "RELEASED" state')
    elif r.json()['_embedded']['signalCollections'][0]['state'] == "DRAFT":
        context.signal_collection_id = r.json()['_embedded']['signalCollections'][0]['signalCollectionId']
        api_rm_obj.release_signal_collection(context.signal_collection_id)
    else:
        assert False, "Signal collection is in "+ r.json()['_embedded']['signalCollections'][0]['state']+" and can't be released"


@step('create a measurement configuration with name "{measurement_configuration_name}", description "{measurement_description}"')
@step('create measurment configuration "{measurement_configuration_name}" if it not is available')
@step('create measurement configuration "{measurement_configuration_name}" using upload interval "{upload_interval:d}" if it is not available')
@step('create measurement configuration "{measurement_configuration_name}" of type "{configuration_type}" if it is not available')
@step('create measurement configuration "{measurement_configuration_name}" of type "{configuration_type}" and timeout {timeout:d} if it is not available')
@step('create a measurement configuration')
def step_impl(context, measurement_configuration_name=None, measurement_description=None, configuration_type="CONTINUOUS", timeout=60000, upload_interval=30):
    """Descirption : Check if the Measurement Configuration is available or else create it

    Pre-condition : None
    
    Parameters  : 
        measurement_configuration_name : The measurement configuration which need to be used     
        measurement_description : Description
        configuration_type : CONTINUOUS / SINGLE_SHOT
        timeout : None for CONTINUOUS ; Defined value for SINGLE_SHOT
        upload_interval : Measurement upload interval, default=60
    Expected result : 
        measurement_configuration_id :  Id of the measurement configuration

    Note : Additional step to create a new measurement configuration needs to be done
    
    """
    measurement_timeout=0
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    context.measurement_configuration_id = api_rm_obj.get_measurement_configuration_id(measurement_configuration_name)
    
    if context.measurement_configuration_id is None:
        if measurement_configuration_name is None:
            context.measurement_configuration_name =  'testMeasurement_' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        else:
            context.measurement_configuration_name = measurement_configuration_name
        if measurement_description is None:
            context.measurement_description = context.measurement_configuration_name
        if configuration_type == "SINGLE_SHOT":
            data = {'name': context.measurement_configuration_name,
                'description': context.measurement_description,
                'timeout': timeout,
                'type': configuration_type}
        elif configuration_type == "CONTINUOUS":
            data = {'name': context.measurement_configuration_name,
                'description': context.measurement_description,
                'uploadInterval' : upload_interval,
                'type': configuration_type}
        r = api_rm_obj.create_measurement_configuration(constants.RM_MEASURE_CONFIG, data)
        assert r.status_code == requests.codes.created, api_gen_obj.assert_message(r)
        context.measurement_configuration_id = api_rm_obj.get_measurement_configuration_id(context.measurement_configuration_name)
    elif (configuration_type=="SINGLE_SHOT" and timeout!=0):
        measurement_timeout= api_rm_obj.get_measurement_timeout(context.measurement_configuration_id)
        context.measurement_configuration_name = measurement_configuration_name
        logging.info(f'Measurment configuration {measurement_configuration_name} is already present')
        if measurement_timeout != timeout:
            api_rm_obj.edit_measurement_timeout(context.measurement_configuration_id, timeout)
            logging.info(f'Measurment configuration {measurement_configuration_name} timeout is editted from {measurement_timeout} to {timeout}')
    else:
        context.measurement_configuration_name = measurement_configuration_name
        logging.info(f'Measurment configuration {measurement_configuration_name} is already present')


@step('add sources "{source_names}" to "{measurement_configuration_name}"')
def step_impl(context,source_names,measurement_configuration_name):
    """
        Add signal collection/s to Measurement Configuration

        Parameters : 
            source_names : Signal collections 
            measurement_configuration_name : Measurement Configuration 
    """
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    api_gen_obj = API_Generic_Class.ApiGenericClass()

    measurement_configuration_id = api_rm_obj.get_measurement_configuration_id(measurement_configuration_name)
    if measurement_configuration_id is not None:
        source_in_measurement_configuration =[]
        r = api_rm_obj.get_measurement_config_source(measurement_configuration_id)
        if '_embedded' in r.json():
            for source in r.json()['_embedded']['sources']:
                source_in_measurement_configuration.append(source['name'])
            logging.info(source_in_measurement_configuration)
        else:
            logging.info(f'{measurement_configuration_name} doesn\'t contain any sources')
        source_collection = source_names.split(",")
        context.source_collection = source_collection
        api_rm_obj.add_sources_to_rm_config(source_collection, source_in_measurement_configuration, measurement_configuration_name, measurement_configuration_id, api_gen_obj)
    else:
        assert False, measurement_configuration_name + ' is not found in Measurement configuration list'


@step('Remove source "{source_names}" from "{measurement_configuration_name}"')
@step('Remove all sources from "{measurement_configuration_name}"')
def step_impl(context, measurement_configuration_name, source_names=None):
    """
        Description: Removes signal collection / source from RM configuration

        Parameters : 
            source_names : Signal collections name(s)
            measurement_configuration_name : Measurement Configuration name to act upon

        Expected: Passed source_names should be removed from RM Configuration
    """
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    context.measurement_configuration_id = api_rm_obj.get_measurement_configuration_id(measurement_configuration_name)
    r = api_rm_obj.get_measurement_config_source(context.measurement_configuration_id)
    
    if(source_names is not None):
        rm_sources = source_names.split(",")
    else:
        if '_embedded' in r.json():
            total_sources=0
            rm_sources=[]
            while total_sources < len(r.json()['_embedded']['sources']):
                rm_sources.append(r.json()['_embedded']['sources'][total_sources]['name'])
                total_sources+=1
        else:
            logging.info("RM configuration doesn't have any assigned Signal colelction / Source.")

    api_rm_obj.fetch_source_id_and_remove_rm_sources(context, r, rm_sources)
        
@step('add "{signals}" to "{measurement_configuration_name}"')
@step('add signals "{signals}" of "{source_name}" to "{measurement_configuration_name}"')
def step_impl(context,signals,measurement_configuration_name,source_name=None):
    """
        
    """
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    context.measurement_configuration_id = api_rm_obj.get_measurement_configuration_id(measurement_configuration_name)
    r = api_rm_obj.get_measurement_config_source(context.measurement_configuration_id)
    source_id = ''
    if '_embedded' not in r.json():
            assert False,' No sources found under' + measurement_configuration_name
    else:
        signal_collection_id, source_id = api_rm_obj.retrieve_signal_collection_source_id(source_name, r, source_id, measurement_configuration_name)

        signal_array = signals.split(",")
        for signal_name in signal_array:
            r = api_rm_obj.get_signal_details_in_signal_collection(signal_collection_id,signal_name)
            if '_embedded' not in r.json():
                assert False, f'{signal_name} is not present in signal_collection_name'
            else:
                signal_id = r.json()['_embedded']['signals'][0]['signalId']
                r = api_rm_obj.add_signal(context.measurement_configuration_id,source_id,signal_id)
                if r.status_code == requests.codes.precondition_failed:
                    logging.info(f'Signal {signal_name} is already selected for {source_name} in {measurement_configuration_name} measurement configuration------------- ')
                elif r.status_code == requests.codes.created:
                    logging.info(f'{signal_name} signal is selected for {source_name} in {measurement_configuration_name} measurement configuration')
                else:
                    assert False, f'Error message : {r.json()["message"]} is diplayed while selecting "{signal_name} signal for {source_name} source in {measurement_configuration_name} measurement configuration"'

@step('add signals "{signals}" of source "{source_name}" to measurement configuration "{measurement_configuration_name}"')
def step_impl(context,signals,measurement_configuration_name,source_name=None):
    """
        Description: Add signals from sources linked to a measurement configuration

        Parameters :
            signals : key-value pair of signal name(s) and corresponding downsampling rate(s) Eg: 'GPS:5000,S_S_STD_0x201_S8:10'
            source_names : Signal collections name(s)
            measurement_configuration_name : Measurement Configuration name to act upon

        Expected: Passed source_names should be removed from RM Configuration
    """
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    context.measurement_configuration_id = api_rm_obj.get_measurement_configuration_id(measurement_configuration_name)
    source_details = api_rm_obj.get_measurement_config_source(context.measurement_configuration_id)
    source_id = ''
    # Validation if source is present in measurement configuration
    signal_collection_id, source_id = api_rm_obj.retrieve_signal_collection_source_id(source_name, source_details, source_id, measurement_configuration_name)

    signal_array = signals.split(",")
    try :
        selected_signals = api_rm_obj.get_measure_config_signals(context.measurement_configuration_id)
    except KeyError as error:
        if '_embedded' in str(error):
            selected_signals = []
    if selected_signals != [] and  context.added_signals == []:
        selected_signals = api_rm_obj.remove_unwanted_signal_from_config(context.measurement_configuration_id, selected_signals, signal_array)
    # Iteration through signals to select them for measurement configuration
    for signal in signal_array:
        signal_name = signal.split(':')[0]
        signal_downsampling = signal.split(':')[1]
        # Validation if signal is present in signal collection
        signal_details = api_rm_obj.get_signal_details_in_signal_collection(signal_collection_id,signal_name)
        if '_embedded' not in signal_details.json():
            assert False, f'{signal_name} is not present in signal_collection_name'
        else:
            signal_id = signal_details.json()['_embedded']['signals'][0]['signalId']
            signal_collection_id = signal_details.json()['_embedded']['signals'][0]['signalCollectionId']
            signal_found = False
            signal_found = api_rm_obj.find_signal_rectify_downsampling(
                signal_id, source_id, signal_collection_id, context.measurement_configuration_id, selected_signals, signal_downsampling)
            if not signal_found:
                r = api_rm_obj.add_signal(context.measurement_configuration_id,source_id,signal_id, signal_downsampling)
                context.added_signals.append(signal)
                assert r.status_code == requests.codes.created, api_gen_obj.assert_message(r)

@step('add messages "{messages}" of source "{source_name}" to measurement configuration "{measurement_configuration_name}"')
def step_impl(context,messages,measurement_configuration_name,source_name=None):
    """
        Description: Add message from sources linked to a measurement configuration

        Parameters :
            signals : key-value pair of message name(s) and corresponding downsampling rate(s) Eg: 'GPS:5000,F_EXT_0x1000001:'
            source_names : Signal collections name(s)
            measurement_configuration_name : Measurement Configuration name to act upon

        Expected: Passed message_name should be added to RM Configuration
    """
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    context.measurement_configuration_id = api_rm_obj.get_measurement_configuration_id(measurement_configuration_name)
    source_details = api_rm_obj.get_measurement_config_source(context.measurement_configuration_id)
    source_id = ''
    # Validation if source is present in measurement configuration
    signal_collection_id, source_id = api_rm_obj.retrieve_signal_collection_source_id(source_name, source_details, source_id, measurement_configuration_name)

    message_array = messages.split(",")
    try :
        selected_messages = api_rm_obj.get_measure_config_selected_messages(context.measurement_configuration_id)
    except KeyError as error:
        if '_embedded' in str(error):
            selected_messages = []
    # Iteration through messages to select them for measurement configuration
    for message in message_array:
        message_name = message.split(':')[0]
        logging.info(f'message_name {message_name}')
        message_downsampling = message.split(':')[1]
        # Validation if message is present in signal collection
        message_details = api_rm_obj.get_messages_of_signal_collection(signal_collection_id,message_name)
        if '_embedded' not in message_details.json():
            assert False, f'{message_name} is not present in signal_collection_name'
        else:
            message_id = message_details.json()['_embedded']['messages'][0]['messageId']
            logging.info(f'message_id {message_id}')
            signal_collection_id = message_details.json()['_embedded']['messages'][0]['signalCollectionId']
            message_found = False
            message_found = api_rm_obj.find_message_rectify_downsampling(
                message_id, source_id, signal_collection_id, context.measurement_configuration_id, selected_messages, message_downsampling)
            if not message_found:
                r = api_rm_obj.add_message(context.measurement_configuration_id,source_id,message_id, message_downsampling)
                assert r.status_code == requests.codes.created, api_gen_obj.assert_message(r)

@step('Remove "{signals}" from "{measurement_configuration_name}"')
@step('Remove signals "{signals}" of "{source_name}" to "{measurement_configuration_name}"')
def step_impl(context,signals,measurement_configuration_name,source_name=None):
    """
        
    """
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    context.measurement_configuration_id = api_rm_obj.get_measurement_configuration_id(measurement_configuration_name)
    r = api_rm_obj.get_measurement_config_source(context.measurement_configuration_id)
    source_id = ''
    if '_embedded' not in r.json():
            assert False,' No sources found under' + measurement_configuration_name
    else:
        signal_collection_id, source_id = api_rm_obj.retrieve_signal_collection_source_id(source_name, r, source_id, measurement_configuration_name)

        signal_array = signals.split(",")
        for signal_name in signal_array:
            r = api_rm_obj.get_signal_details_in_signal_collection(signal_collection_id,signal_name)
            if '_embedded' not in r.json():
                assert False, f'{signal_name} is not present in signal_collection_name'
            else:
                signal_id = r.json()['_embedded']['signals'][0]['signalId']
                api_rm_obj.remove_signal(context.measurement_configuration_id,source_id,signal_id)

@step('verify number of "{measurement_entity}" are "{count}" respectively is present in measurement configuration "{measurement_configuration_name}"')
def step_impl(context, count, measurement_entity, measurement_configuration_name):

    """Description : Verify number of Signals, Messages, calculated signals or triggers present in a measurement configuration

    Pre-condition : None

    Parameters : count : number of signals or messages, calculated signals or triggers separated with ","
                 measurement_entity : either signals, messages, calculatedSignals or triggers
    
    Expected results : verifies the number of signals, messages, calculated signals or triggers else step fails with actual count

    """
    context.measurement_configuration_list=[]
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    if ('update_meas_config_name' in context): # 'if condition' will be removed once implementing NON-NGD changes for regression/load/installatoin scenario
        measurement_configuration_name = context.update_meas_config_name
    context.measurement_configuration_list.append(measurement_configuration_name)
    context.measurement_configuration_name= measurement_configuration_name
    context.measurement_configuration_id = api_rm_obj.get_measurement_configuration_id(measurement_configuration_name)
    
    api_rm_obj.verify_measurement_entity_count(context.measurement_configuration_id,measurement_entity,count)

@step('Verify Measurement job "{measurement_configuration_name}" can be set to "{state}" state')
@step('Verify Measurement job "{measurement_configuration_name}" can be set to "{state}" state returns {status}')                    
@step('Measurement job "{measurement_configuration_name}" is in "{state}" state')
@step('release measurement configuration "{measurement_configuration_name}"')
def step_impl(context,measurement_configuration_name=None,state="RELEASED",status="Success"):
    
    """Descirption : Move the measurement configuration to either created or draft state

    Pre-condition : 
        none
    
    Parameters  : 
        measurement_configuration_name : Mandetory and required for the change of state of this configuration
        stae : either released or draft, default state is "released"
   
    Expected result : 
        r :  status code is ok if the measurement data is deleted successfully
    
    """    
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    if ('update_meas_config_name' in context): # 'if condition' will be removed once implementing NON-NGD changes for regression/load/installatoin scenario
        measurement_configuration_name = context.update_meas_config_name
    if measurement_configuration_name is not None:
        context.measurement_configuration_id = api_rm_obj.get_measurement_configuration_id(measurement_configuration_name)
    else:
        assert False, "Measurement configuration is not available"

    if context.measurement_configuration_id is None:
        assert False, "Configuration ID is not available"        

    meas_conf_state = api_rm_obj.get_measurement_configuration_details(context.measurement_configuration_id)
    state_changed = False
    if meas_conf_state == state.upper():
        logging.info(f'{measurement_configuration_name} is already in {state} state')
    elif meas_conf_state == "RELEASED":
        context.meas_config_version = api_rm_obj.get_latest_measurement_config_version(context.measurement_configuration_id)
        api_rm_obj.set_measurement_configuration_state(context.measurement_configuration_id, "draft")
    elif meas_conf_state == "DRAFT":
        if hasattr(context, 'has_invalid_signals') and status != 'Success':
            try:
                state_changed = api_rm_obj.set_measurement_configuration_state(context.measurement_configuration_id, "releases")
                updated_meas_config_version = api_rm_obj.get_latest_measurement_config_version(context.measurement_configuration_id)
                assert updated_meas_config_version > context.meas_config_version, f"Unexpected RM configuration version appeared, Expected version : {updated_meas_config_version} , but current version: {context.meas_config_version}"
            except Exception as exception:
                logging.info(exception)
            assert not state_changed, f"Measurement configuration with invalid signals is set to released state, which is not expected"
        else:
            api_rm_obj.set_measurement_configuration_state(context.measurement_configuration_id, "releases")
            updated_meas_config_version = api_rm_obj.get_latest_measurement_config_version(context.measurement_configuration_id)
            assert updated_meas_config_version > context.meas_config_version, f"Unexpected RM configuration version appeared, Expected version : {updated_meas_config_version} , but current version: {context.meas_config_version}"
    else:
        assert False, "State of Measurement configuration can not be changed"


@step('verify that invalid calculated signal is "{present}" in measurement configuration "{measurement_configuration_name}"')
def step_impl(context,present,measurement_configuration_name=None,):
    """Description : To verify that measurement configuration has invalid signals
       
       pre-condition :
                      create measurement configuration <meas_config_name> if it is not available

       parameters    :measurement_configuration_name,
                      flag=true/false
        
       Expected result : It evaluates invalid signals in the measurement_configuration_name
        
     """

    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)

    if measurement_configuration_name is not None:
        context.measurement_configuration_id = api_rm_obj.get_measurement_configuration_id(measurement_configuration_name)
    else:
        assert False, "Measurement configuration is not available"
    
    context.has_invalid_signals=api_rm_obj.get_invalid_signals_status(context.measurement_configuration_id)
    assert eval(present)==context.has_invalid_signals, f"Measurement configuration invalid signal state is {context.has_invalid_signals} but expected is {present} "
        
@step('delete the newer measurement data')
def step_impl(context):
    """Description : Delete newer measurement data and the data older than 48 hours associated with this vehicle

    Pre-condition : 
                    device "{device_id}" is mapped to vehicle "{vehicle_name}"
                    measurement is activated
                    measurement status is "{status}" within "{timer}" minutes
                    
    Parameters  : None        
   
    Expected result : 
        r :  status code is ok if the measurement data is deleted successfully
    
    """
    past_rm_test_step_time_hr = 48
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    api_rm_obj.delete_vehicle_rm_test_step(context.vehicle_id, context.rm_activation_date, past_rm_test_step_time_hr)

@step('Remote measurement "{measurement_configuration}" is activated for vehicle setup group "{vsg_name}"')
def step_impl(context, vsg_name = None, measurement_configuration = None):
    """ Descirption : activate remote measurement with given vehicle

    Pre-condition : 
        device "{device_id}" is mapped to vehicle "{vehicle_name}"
        create measurment configuration "{meas_config_name}" if it not is available
    
    Parameters  : None        
   
    Expected result : 
        status_code :  status code is ok if the measurement data is deleted

        status : Need to be ACTIVE once measurement is started

        substatus : Need to be ACTIVATION_CONFIRMED once measurement is started
    
    """
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    context.vsg_device_slot = context.all_vsg_data[vsg_name]["device_slot"][0]
    context.slot_assignment_id=[]
    if ('update_meas_config_name' in context): # 'if condition' will be removed once implementing NON-NGD changes for regression/load/installatoin scenario
        measurement_configuration = context.update_meas_config_name
    context.measurement_configuration_list=measurement_configuration.split(',')
    for measurement_configuration in context.measurement_configuration_list:
        start_time = datetime.datetime.now(datetime.timezone.utc)
        measurement_configuration_id = api_rm_obj.get_measurement_configuration_id(measurement_configuration)            
        api_rm_obj.trigger_vsg_measurement_activation(context.vsg_id, context.vsg_device_slot, measurement_configuration_id)
        vsg_assignment = api_rm_obj.get_vsg_rm_assignment_detail(context.vsg_id, measurement_configuration_id, context.vsg_device_slot)
        slot_assignment_id = vsg_assignment['mc2SlotAssignmentId']
        context.slot_assignment_id.append(slot_assignment_id)
        measurement_data={'id': measurement_configuration_id,'activated': True,'vsg_slot_assignment_id':slot_assignment_id}
        context.all_vsg_data[vsg_name]['remote_measurements'][measurement_configuration]=measurement_data
        logging.info(f'Measurement Configuration {measurement_configuration} Activation triggered on Vehicle Setup Group %s'%vsg_name)
        time.sleep(60) # After RM VSG activation, it takes 10 - 20 seconds to get measurement_job_id for vehicles
        context.vsg_rm_status = True
        for vehicle in context.vehicle_data:                
            vehicle_id = context.vehicle_data[vehicle]["vehicle_id"]
            if len(context.vehicle_data[vehicle]["device_data"]) != 0:
                assignment_details = api_rm_obj.get_measurement_assignment_details(vehicle_id, measurement_configuration_id, context.vsg_device_slot)
                context.assignment_job_id = assignment_details['mc2SlotAssignmentId']
                context.vehicle_data[vehicle]["remote_measurement"][measurement_configuration]={}
                context.vehicle_data[vehicle]["remote_measurement"][measurement_configuration].update({"rm_job_id"+context.vsg_device_slot : context.assignment_job_id})
                context.all_assignment_jobs[context.assignment_job_id] = {'start_time': start_time, 'measurement_start_time': '', 'end_time': '', 'measurement_end_time': '', 'status': ''}
                rm_activation_date = str(start_time).split(".")
                rm_activation_date = datetime.datetime.strptime(rm_activation_date[0],"%Y-%m-%d %H:%M:%S")
                if context.rm_activation_date =="":
                    context.first_rm_activation_date=rm_activation_date
                context.rm_activation_date = context.vehicle_data[vehicle]["remote_measurement"][measurement_configuration].update({"rm_activation_date" : rm_activation_date})
    context.all_vsg_data[vsg_name]['remote_measurements']['all_assignment_ids']=context.slot_assignment_id

@step('data integrity test is performed on consecutive frames')
@step('data integrity test is performed for the {number:d} numbereth test step result')
@step('data integrity test is performed on all the results')
def step_impl(context, number = 1):
    """ Descirption : Perform tests to verify the duration of test, value check for each variable and timestamp check for each variable

    Pre-condition : 
        test results are verified

        test is executed for "{min}" minutes

        Remote measurement is activated

        Remote measurement is deactivated

    Parameters  :   number(OPTIONAL) - Integer
                        The nth number of test step to be validate for data integrity(only if the number of test steps are greater than 1)       
   
    Expected result : 
        1. The data integrity of the downloaded csv is intact for all test steps
        2. The data integrity of the downloaded csv is intact of the 'n'th test step
    
    """    
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    if (hasattr(context, 'test_duration') is not True):
        # Timestamps of latest measurement job activated(Measurment job which was activated in the last)
        measurement_end_time   = context.all_assignment_jobs[list(context.all_assignment_jobs)[-1]]['measurement_end_time']
        measurement_start_time = context.all_assignment_jobs[list(context.all_assignment_jobs)[-1]]['measurement_start_time']
        duration = measurement_end_time - measurement_start_time
        duration_in_ms = duration.total_seconds()*1000
        context.test_duration = duration_in_ms
        logging.info(f'Measurement was active for a duration of {str(context.test_duration/1000)} seconds')
    end_time = context.all_assignment_jobs[list(context.all_assignment_jobs)[-1]]['end_time']
    start_time = context.all_assignment_jobs[list(context.all_assignment_jobs)[-1]]['start_time']
    if number > 1 :
        r = api_rm_obj.validate_measurement_duration([context.test_result[number - 1]], start_time , end_time, context.test_duration)
    else :
        r = api_rm_obj.validate_measurement_duration(context.test_result, start_time , end_time, context.test_duration)
    assert r is True, "Result is not current or test duration is not correct"        
    for row in context.table:        
        r = api_rm_obj.time_stamp_check(context.test_result, row["Variable"], row["Timestamp"], row["Threshould"])
        assert r is True, "Either variable is not present or timestamp check failed"
        r = api_rm_obj.value_check(context.test_result, row["Variable"], row["Increment"])
        assert r is True, "Either variable {} is not present or value check failed"

#@step('Remote measurement is deactivated')    
#@step('Remote measurement {measurement_config_name} is deactivated')
# def step_impl(context, measurement_config_name=None): 
#     """ 
#         Descirption : deactivate remote measurement with given vehicle

#         Pre-condition : 
#         device "{device_id}" is mapped to vehicle "{vehicle_name}"
#         create measurment configuration "{meas_config_name}" if it not is available
    
#         Parameters  : None        
   
#         Expected result : 
#         status_code :  status code is ok if the measurement data is deleted

#         status : Need to be INACTIVE once measurement is stopped

#         substatus : Need to be DEACTIVATION_CONFIRMED once measurement is stopped
    
#     """    
#     print ("=======================================================================================")
#     print("Deactivating measurement job")
#     print ("=======================================================================================")

#     api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
#     def deactivate_by_job_id(measurement_job_id):
#         measurement_status = api_rm_obj.check_measurement_status(context.vehicle_id, measurement_job_id, "ACTIVE")    
#         assert measurement_status[0][len(measurement_status[0])-1] == "ACTIVE", "Unexpected. Measurement current Status - %s, so cannot be de-activated"%measurement_status[0][len(measurement_status[0])-1]
#         b_deactivation_status = api_rm_obj.trigger_measurement_deactivation(context.vehicle_id, measurement_job_id)
#         if (b_deactivation_status):
#             print (f"Measurement De-activation for {measurement_job_id} is triggered successfully")
#             print (150*"=")

#     if measurement_config_name is not None:
#         measurement_configuration_id = api_rm_obj.get_measurement_configuration_id(measurement_config_name)
#         measurement_job_id=api_rm_obj.get_measurement_job_id_by_config_id(context.vehicle_id, context.device_id, measurement_configuration_id)
#         deactivate_by_job_id(measurement_job_id)
#     else:
#         if (context.rm_activation_status):
#             count = len(context.all_measurement_jobs)     
#             while count > 0:
#                 first_job_id = list(context.all_measurement_jobs)[len(context.all_measurement_jobs) - count]
#                 if not context.all_measurement_jobs[first_job_id]['status']=='inactive':
#                     deactivate_by_job_id(first_job_id)
#                 count = count - 1
#         else:
#             print('No active remote measurements to be deativated!')

@Step('create signal collection "{dbc_file_name}" with protocol "{protocol}"')
def step_impl(context,dbc_file_name,protocol): 
    """ Descirption : Creates Singnal collection for Remote measurement

        Pre-condition : None  

        Parameters  : DBC file,Prtocol type

        Expected result : 
        status_code :  status code is created 

    """
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details) 
    file_path = os.getcwd() + constants.DATA_J1939 + dbc_file_name
    logging.info(file_path)
    files = {'file': open(file_path, 'rb')}
    context.collection_name = "invalidformateDBC"+datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    new_data = {
        "name":context.collection_name,
        "protocol":protocol,
        "input":"DBC",
        "version":"1",
        "description":""
    }

    r = api_rm_obj.create_signal_collection(constants.RM_SIG_COL,new_data,files)
    assert r.status_code == requests.codes.created,"Collection creation error"
   

@Step('validates FileImportState "{file_import_state}" for signal collcetion')
def step_impl(context,file_import_state): 
    """ Descirption : Validates FileImportState field in Singnal collection details

        Pre-condition : None  

        Parameters  :state to be verified

        Expected result :  Expected states matches 

    """
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details) 
    r = api_rm_obj.get_signal_collection(constants.RM_SIG_COL_SEARCH_NAME.format(context.collection_name))
    assert r.json()['_embedded']['signalCollections'][0]['fileImportState'] == file_import_state,"Single collection state is not as expected"
    
@step('add signals "{signals}" to "{measurement_config}"')
def step_impl(context, signals, measurement_config):
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details) 
    measurement_config_id = api_rm_obj.get_measurement_configuration_id(measurement_config)
    api_rm_obj.draft_measurement_configuration(measurement_config_id)
    api_rm_obj.add_signals(measurement_config_id, signals)


@step('measurement job having "{count}" measurement receives newer measured results')
@step('measurement job having "{count}" measurement receives measured results')
def step_impl(context, count):
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    r = api_rm_obj.get_vehicle_teststep_id(context.vehicle_id)
    assert r.status_code == requests.codes.ok, "Error while fetching Measurement Job information for the vehicle."
    assert len(r.json()['_embedded']['testSteps']) == int(count), "Unexpected. Count of Measurement test steps is wrong. Actual Job Count - "+str(len(r.json()['_embedded']['testSteps']))+" Expected Job Count - "+str(count)

    actual_received_data = r.json()['_embedded']['testSteps'][0]['dataIntegrity']['receivedJobs']
    if int(count) == 2:
        assert actual_received_data > 0, "Unexpected. New measurement data is not generated."
    else:
        assert actual_received_data > context.received_data, "Unexpected. New measurement data is not generated."
    context.received_data = actual_received_data


@step('Perform Remote Measurement {number:d} times with the data {vehicle}, {device}, {measurement_job}, {protocol}, {identifier}, {measurement_entity}, {count}')
def step_impl(context, number, vehicle, device, measurement_job, protocol, identifier, measurement_entity, count):
    """ Description     : it completes the RM assignment for multiple number of times

        Pre-condition       : None

        Parameters          : number, vehicle, device, flashjob_config, protocol, identifier, fota

                            eg. number = 100, vehicle_new = "E2E_SYS_ES740_14", device = "ES740_46100072",
                            flashjob_config = "SYS-I-RF-ES740-Job-delete-after-RF", protocol = "UDSonCAN",
                            identifier = "cTP_RF_SmokeTest", fota = "CANalization", fota_identifier = "Flash_Start_ES740"

        Expected result     : completes Remote Flashing multiple number of times over and over again on the same device
    """
    context.execute_steps(f'''
      Given device {device} is "ONLINE"
      And map device to the {vehicle} if there are no pending {measurement_job} measurement jobs
      And reference system {protocol} with Identifier {identifier} is started
      And verify number of {measurement_entity} are {count} respectively is present in measurement configuration {measurement_job}
      And release measurement configuration {measurement_job}
    ''')

    context.repetitive_steps = f'''
                Given device {device} is "ONLINE"
                When Remote measurement is activated
                And measurement status is "ACTIVE" within "10" minutes
                And test is executed for "2" minutes
                Then Remote measurement is deactivated
                And measurement status is "INACTIVE" within "10" minutes
                And measurement test results are stored
                And measurement data integrity smoke test is performed
                And test waits for "1" minutes
            '''
            
    context.execute_steps(f'''
        Given perform load test for {number} iterations with predefined steps
        Then reference system is stopped
    ''')


@step('map device to the "{vehicle_name}" if there are no pending "{measurement_config}" measurement jobs')
def step_impl(context, vehicle_name, measurement_config):
    """

    """
    context.execute_steps(f'''
            Given prepare vehicle "{vehicle_name}" by clearing all pending jobs
            And map device to the vehicle "{vehicle_name}"
     ''')

@step('Attempt to "{state}" trigger "{trigger}" with pretrigger time as "{pretrigger}" seconds')
@step('Attempt to "{state}" trigger "{trigger}" with pretrigger time as "{pretrigger}" seconds and posttrigger time as "{posttrigger}" seconds')
@step('Attempt to "{state}" trigger "{trigger}"')
@step('Attempt to "{state}" trigger "{trigger}" returns "{status}"')
def step_impl(context, trigger, state, status="Success",pretrigger=0,posttrigger=None):

    """Descirption : Move the measurement configuration to either created or draft state

    Pre-condition : 
        When Measurement job <meas_config_name> is in "draft" state
        Measurement job need to be in draft state as this step will not have measurement configuration name
    
    Parameters  : 
        trigger : This is name, description, pre-trigger and post-trigger value
        state : This is needed to add, edit or delete the trigger
        status : Expected status
   
    Expected result : 
        r :  status code is ok if the measurement data is deleted successfully
    
    """

    api_gen_obj = API_Generic_Class.ApiGenericClass()   
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    trigger_json_data = api_gen_obj.parse_json_file(constants.RM_TRIGGER_JSON)
    context.trigger_json_data = trigger_json_data

    try:
        if state.upper() == "ADD":
            data = trigger_json_data["trigger"][trigger.lower()]
            context.pre_trigger,context.post_trigger,data = api_rm_obj.update_data_with_pre_post_trigger_time(pretrigger,posttrigger,data)
            api_rm_obj.add_trigger(context.measurement_configuration_id, data)
        elif state.upper() == "EDIT":
            data = trigger_json_data["trigger"][trigger.lower()]
            context.pre_trigger,context.post_trigger,data = api_rm_obj.update_data_with_pre_post_trigger_time(pretrigger,posttrigger,data)
            api_rm_obj.edit_trigger(context.measurement_configuration_id, data)
        elif state.lower() == "delete":
            api_rm_obj.del_trigger(context.measurement_configuration_id)
        elif state.upper() == "ACTIVATE" or state.upper() == "DEACTIVATE":
            api_rm_obj.set_trigger_state(context.measurement_configuration_id, state.lower())
        else:
            assert False, "State is not correct"
    
    except Exception as e:
        if status.upper() == "SUCCESS":
            assert False, "Error in {}ing trigger : {}".format(state.upper(),e)
        else:
            assert False, "Test {}s erroneous trigger".format(state.upper())


@step('verify trigger "{trigger}" is "{state}"ed successfully')
def step_impl(context, trigger, state):
    api_gen_obj = API_Generic_Class.ApiGenericClass()   
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)

    if (not hasattr(context, 'trigger_json_data')):
        trigger_json_data = api_gen_obj.parse_json_file(constants.RM_TRIGGER_JSON)
        context.trigger_json_data = trigger_json_data
    data = context.trigger_json_data["trigger"][trigger.lower()]
    data["preTriggerTime"]=context.pre_trigger
    if "postTriggerTime" in data:
        data["postTriggerTime"]=context.post_trigger

    actual_trigger_info = api_rm_obj.get_trigger_info_of_mc(context.measurement_configuration_id)
    logging.info("Comparing Created Trigger with the Expected Trigger values...")
    for key in data:
        assert data[key] in actual_trigger_info.values(), "Created trigger value doesn't match. Expected Value - %s:%s"%(key,data[key])

    context.trigger_id = actual_trigger_info['triggerId']
    context.pre_trigger_time = actual_trigger_info['preTriggerTime']
    if "postTriggerTime" in data:
        context.post_trigger_time = actual_trigger_info['postTriggerTime']


@step('Attempt to "{state}" the "{trigger_phase}"')
@step('Attempt to "{state}" the "{trigger_phase}" returns "{status}"')
@step('Attempt to "{state}" the "{trigger_phase}" with "{element}" returns "{status}"')
def step_impl(context, trigger_phase, state, status="SUCCESS", element=None):
    """Descirption : Move the measurement configuration to either created or draft state

    Pre-condition : 
        Verify Trigger "{trigger}" can be "{state}" with "{status}"
        Trigger need to be increated state to add, edit or remove start or stop trigger
    
    Parameters  : 
        trigger : This is name, description, pre-trigger and post-trigger value
        state : This is needed to add, edit or delete the trigger
        status : Expected status
   
    Expected result : 
        r :  status code is ok if the measurement data is deleted successfully
    
    """

    api_gen_obj = API_Generic_Class.ApiGenericClass()   
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    trigger_condition_name = []
    

    if (not hasattr(context, 'trigger_json_data')):
        trigger_json_data = api_gen_obj.parse_json_file(constants.RM_TRIGGER_JSON)
        context.trigger_json_data = trigger_json_data

    if state.upper() == "ADD" or state.upper() == "EDIT":
        trigger_payload = {}

        #smb7kor
        api_rm_obj.add_or_edit_trigger_element(context, element, trigger_phase, trigger_payload, state, status, trigger_condition_name)

    elif state.lower() == "delete":
        try:
            api_rm_obj.del_trigger_element(context.measurement_configuration_id, trigger_phase)
        except Exception as e:
            if status.upper() == "SUCCESS":
                assert False, "Error in deleting trigger phase : {}".format(e)
            else:
                if status.upper() != "SUCCESS":
                    assert False, "Test edit deleting trigger phase"

    else:
        assert False, "state is not correct"


@step('verify trigger condition "{trigger_phase}" is "{state}"ed successfully')
def step_impl(context, trigger_phase, state):

    logging.info(f"fetching and verifying {state}ed {trigger_phase} details...")
    
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    r = api_rm_obj.get_trigger_condition_details(context.measurement_configuration_id, context.trigger_id, trigger_phase)
    # assert 'name' in r.json(), "Unexpected. Trigger Condition group is not present."
    # assert r.json()["name"] == context.exp_trigger_name, "%s condition group name appears wrong. Actual - %s. Expected - %s"%(trigger_phase,r.json()["name"],context.exp_trigger_name)
    # assert len(r.json()["triggerElements"]) == len(context.trigger_condition_name), "Unequal count of trigger conditions exist. Actual Count - %s, Expected Count - %s"%(len(r.json()["triggerElements"]),len(context.exp_trigger_condition_names))
    # for condition_name in r.json()["triggerElements"]:
    #     assert condition_name["name"] in context.trigger_condition_name, "Wrong %s condition is created. Trigger condition name: Actual - %s. Expected - %s"%(trigger_phase,condition_name["name"],context.exp_trigger_condition_names)
    api_rm_obj.compare_trigger_data(r.json(),context.expected_data_dict[trigger_phase])

    if (trigger_phase == "startTrigger") :
        context.start_trigger = r.json()
    elif (trigger_phase == "stopTrigger") :
        context.stop_trigger = r.json()


@step('trigger "{trigger}" is in "{status}" state')
def step_impl(context,trigger,status):
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    try:
        act_status = api_rm_obj.get_trigger_status(context.measurement_configuration_id)
    except Exception as e:
        assert False, "Error in getting trigger status : {}".format(e)
    else:
        if status.upper() != act_status:
            assert False, ' Expected Status = {} and Actual Status = {}'.format(status.upper(),act_status)



@step('data integrity test is performed on measured data as per trigger condition "{trigger_condition_name}"')
@step('data integrity test is performed on measured data as per trigger "{trigger}" trigger condition "{trigger_condition_name}" for trigger type "{trigger_type}"')
@step('data integrity test is performed on measured data for "{trigger_phase}" trigger as per trigger "{trigger}" trigger condition "{trigger_condition_name}" for trigger type "{trigger_type}"')
def step_impl(context, trigger_condition_name,trigger_type=None, trigger_phase=None, trigger=None):
    """ 
    Description : Perform tests to verify the duration of test, monotony value check for each variable and timestamp check for each variable
                  And also perform validation test based on trigger mode.
        Pre-condition : 
        test results are verified

        test is executed for "{min}" minutes

        Remote measurement is activated

        Remote measurement is deactivated

    Parameters  : trigger condition name(descripted inside trigger.json), trigger mode name and trigger phase - start/stop trigger       
   
    Expected result : 
        r: Boolean, true if a particular test has passed
    
    """    
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    api_gen_obj = API_Generic_Class.ApiGenericClass()   

    json_data = api_gen_obj.parse_json_file(constants.RM_TRIGGER_JSON)
    if trigger_type == "TIME_INTERVAL":
        exp_measurements = json_data['triggerTestData'][trigger_condition_name]['startTrigger']['triggerElements']
    else:
        exp_measurements = json_data['triggerTestData'][trigger_condition_name]["Validation"]
    for exp_measurement in exp_measurements:
        if trigger_type in constants.RM_TRIGGER_MODE:
            api_rm_obj.trigger_measured_value_check(trigger_type,exp_measurement,trigger_phase,context)
        elif trigger_type=="TIME_INTERVAL":
            api_rm_obj.trigger_measured_time_check(trigger_type,context.rm_activation_date,context.vehicle_id,exp_measurement,trigger_phase,context)
        elif trigger_type=="APPEARS":
            api_rm_obj.measured_message_appear_check(exp_measurement,trigger_phase,context)
        elif trigger_type=="VEHICLE_PROPERTY":
            api_rm_obj.trigger_measured_timestamp_check(exp_measurements,context)
        elif trigger_type == "DM1_Message":
            api_rm_obj.trigger_measured_value_check(trigger_type,exp_measurement,trigger_phase,context)
            api_rm_obj.validate_dm1_messages(json_data['triggerTestData'][trigger_condition_name], context.measurement_configuration_id, context.measurement_test_result)

    trigger_type_list = ["Daf_Warnings","Tell_Tales","DM1_Extend_Message"]

    if trigger_type in trigger_type_list:
        measurement_test_result=context.measurement_test_result
        data_validation_index = 0
        for teststep_id in list(measurement_test_result.keys()):
            logging.info(teststep_id)
            result = measurement_test_result[teststep_id]
            data_array=result['results']['data']
            api_rm_obj.verify_calculated_list_signals_data(data_array, context.measurement_configuration_id,data_validation_index, None, trigger_condition_name,trigger_type)
            data_validation_index += 1
        
@step('verify attempt to "{state}" trigger "{trigger}" is rejected')
def step_impl(context, state, trigger):
    """
        Descirption : Step covers the negative scenario of trying to activate trigger having improper trigger conditions

        Pre-condition : 
           Attempt to "Add" trigger <Trigger>
    
        Parameters  : 
            trigger : Name of trigger that is required to be (de)activated 
            state : "ACTIVATE" / "DEACTIVATE"
   
        Expected result : 
            Checking the response code for the PUT request
    """
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    api_request = API_Requests.ApiRequestsClass(context.env, context.log_api_details)
    
    trigger_id = api_rm_obj.get_trigger_id_of_mc(context.measurement_configuration_id)
    etag = api_request.get_etag(constants.RM_MEASURE_CONFIG_ID.format(context.measurement_configuration_id))
    r = api_request.put_request(constants.RM_MEASURE_CONFIG_ID_TRIGGERS_ID_PHASE.format(context.measurement_configuration_id,trigger_id,state.lower()), params={}, custom_header={'if-match': etag})
    assert r.status_code == requests.codes.precondition_failed, "Status code: {}, Message: {}".format(r.json()["status"],r.json()["detail"])
    logging.info("As trigger Group / Condition is not present, so activating Trigger is rejected successfully.")

@step('add calculated signals "{calculated_signals}" with invalid formula "{formula}" respectively to measurement configuration "{measurement_configuration_name}"')
def step_impl(context,calculated_signals,formula,measurement_configuration_name):
    """ Description : Add calculated signals with defined formulas
       
       Pre-condition : create measuerment configuration <meas_config_name> if it is not available

       Parameters  : calculated_signals : key-value pair of calculated signal name(s) and corresponding downsampling rate(s) Eg: 'Calc_signal_1:5000,Calc_signal_2:10'
                     formula : JSON with predefined Name, Unit, desc, formula
                     measurement_configuration_name

       Expected result : Calculated signals are created with formula

    """
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    api_gen_obj = API_Generic_Class.ApiGenericClass()   

    json_data = api_gen_obj.parse_json_file(constants.OTA_VEHICLE_DATA_CALCULATED_SIGNAL_JSON_PATH)
    context.measurement_configuration_id = api_rm_obj.get_measurement_configuration_id(measurement_configuration_name)
    calculated_signal_array = calculated_signals.split(",")
    formula_name_array = formula.split(",")
    try :
        selected_calculated_signals = api_rm_obj.get_measure_config_calculated_signals(context.measurement_configuration_id)
    except KeyError as error:
        if '_embedded' in str(error):
            selected_calculated_signals = []
    if selected_calculated_signals!=[]:
        api_rm_obj.remove_calculated_signals(context.measurement_configuration_id,selected_calculated_signals)
    index = 0
    for calculated_signal in calculated_signal_array:
        calculated_signal_name = calculated_signal.split(':')[0]
        calculated_signal_downsampling = calculated_signal.split(':')[1]
        if calculated_signal_downsampling == "":
            calculated_signal_downsampling = "0"
        formula = json_data[formula_name_array[index]]
        api_rm_obj.add_calculated_signal_with_formula(context.measurement_configuration_id,calculated_signal_name, calculated_signal_downsampling,formula)
        index+=1   

@step('measurement test result downloads are reprepared')
def step_impl(context):
    """ Descirption : Prepares the CSV download for RM measurement Test Steps
                        
    Pre-condition : 
        device "{device_id}" is mapped to vehicle "{vehicle_name}"

    Parameters  :   NA
   
    Expected result : 
        RM Test steps download is prepared
    """
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    previous_measurement_result = {}

    if (hasattr(context, 'measurement_test_result')):
        previous_measurement_result.update(context.measurement_test_result)
        context.previous_measurement_result = previous_measurement_result

    r = api_rm_obj.get_vehicle_teststep_id(context.vehicle_id)
    assert r.status_code == requests.codes.ok, "Failed to fetch RM Test step details."
    element_count = r.json()['page']['totalElements']
    element = 0
    while (element < element_count):
        test_step_id = r.json()['_embedded']['testSteps'][element]['testStepId']
        total_rm_seconds = api_rm_obj.rm_test_step_time_diff(context.vehicle_id, context.rm_activation_date,r.json()['_embedded']['testSteps'][element]['creationDate'])           
        if total_rm_seconds>0: 
            api_rm_obj.prepare_csv(test_step_id)
            context.rm_download_prepared = True
        element += 1
    
@step('measurement test results having {newer_data} newer measured data is validated')
@step('measurement test results having newer measured data is validated')
def step_impl(context, newer_data="YES"):
    for key_before_reprepare in context.previous_measurement_result:
        for key_after_reprepare in context.measurement_test_result:
            if key_before_reprepare is key_after_reprepare:
                end_time1 = context.measurement_test_result[key_after_reprepare]['end_time']
                end_time2 = context.previous_measurement_result['key_before_reprepare']['end_time']
                if newer_data is "yes".upper():
                    assert end_time2 > end_time1, f"Measurement re-prepare download doesn't have newer measurement data. - Time before reprepare-{end_time1}, Time after reprepare-{end_time2}"
                elif newer_data is "NO".upper():
                    assert end_time2 == end_time1, f"Measurement re-prepare download have newer measurement data. - Time before reprepare-{end_time1}, Time after reprepare-{end_time2}"

#TO DO: should club this step with the above step (shashank)
@step('measurement test results having no loss of measured data is validated')
def step_impl(context):   
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details) 
    gsm_duration_ms = api_fm_obj.calculate_gsm_duration(context.gsm_timer, context.count_timer)
    if context.test_duration_ms_latest_measurement >= gsm_duration_ms:
        logging.info(f'Measurement was recored for the duration of {str(gsm_duration_ms/1000)} seconds')
    else:
        logging.info(f'Measurement was not recored for the duration of {str(gsm_duration_ms/1000)} seconds')

@step('measurement test steps are not generated')
def step_impl(context):
    """
    Description: Step to validate no test steps generation

    Parameters  :   NA 
    
    """
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    context.measurement_test_result = api_rm_obj.get_measurement_results(context.vehicle_id, context.rm_activation_date)
    assert len(context.measurement_test_result) == 0, f'Number of test steps expected to be 0 but is {len(context.measurement_test_result)}'

@step('measurement test results are stored for vehicle setup group "{vsg_name}"')              
@step('measurement test results are stored')
@step('measurement test results are stored including "{preview_data}"')
@step('measurement test results are stored for RM campaign "{campaign_detail}"')
def step_impl(context, vsg_name = None, preview_data = None, campaign_detail = None):
    """ Descirption : Get the test results from the backend in csv format for all the test steps of the vehicle and convert it to json format
                        
    Pre-condition : 
        device "{device_id}" is mapped to vehicle "{vehicle_name}"

    Parameters  :   NA
   
    Expected result : 
        1. Test steps data downloaded
        2. Data is stored in a list of dictionries - {test_step_id : test_result_json}
    
    """
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    download_prepared, preview_prepared = api_rm_obj.verify_rm_download_and_preview_prepared(context)
    
    if vsg_name is None and campaign_detail is None:
        context.measurement_test_result = api_rm_obj.get_measurement_results(context.vehicle_id, context.rm_activation_date, download_prepared, preview_prepared, preview_data)
        assert len(context.measurement_test_result) > 0, f'Number of test steps expected to be at least 1 but is {len(context.measurement_test_result)}'
    elif vsg_name is not None:
        for vehicle in context.vehicle_data:
            vehicle_id = context.vehicle_data[vehicle]["vehicle_id"]
            context.measurement_test_result = api_rm_obj.get_measurement_results(vehicle_id, context.first_rm_activation_date, download_prepared)
            assert len(context.measurement_test_result) > 0, f'Number of test steps expected in {vehicle} to be at least 1 but is {len(context.measurement_test_result)}'
            context.vehicle_data[vehicle]["remote_measurement"].update({"rm_result" : context.measurement_test_result})
    else:
        for vehicle in context.vehicle_data:
            vehicle_id = context.vehicle_data[vehicle]["vehicle_id"]
            for campaign_id in context.activation_campaign_ids:
                if vehicle_id in context.campaign_vehicle_data[campaign_id]["vehicle_ids"]:
                    rm_activation_date = context.vehicle_data[vehicle]["remote_measurement"]["rm_activation_date"+campaign_id+vehicle_id]
                    measurement_test_result = api_rm_obj.get_measurement_results(vehicle_id, rm_activation_date, download_prepared)
                    assert len(measurement_test_result) > 0, f'Number of test steps expected in {vehicle} to be at least 1 but is {len(measurement_test_result)}'
                    context.vehicle_data[vehicle]["remote_measurement"].update({"rm_result"+campaign_id+vehicle_id : measurement_test_result})
        
@step('measurement test result is "{result_exists}"')
@step('measurement test results are present and {number_of_teststeps:d} in number')
@step('measurement test results are verified')
def step_impl(context, result_exists = "True", number_of_teststeps = 1):
    """ Descirption : Verify the number of test steps is the same as expected/
                        Verify the nth number of step contains at lease one data row or not

    Pre-condition : 
        Measurement test results are stored and available in context.measurement_test_result

    Parameters  :   result_exists(OPTIONAL) - True/False
                        True if at least 1 test step is expected. False if no test steps are expected

                    number_of_teststeps(OPTIONAL) - Integer
                        The number of teststeps to be verified for existence

                    number(OPTIONAL) - Integer
                        The numbereth test step to be verified for at least no data
                    
    Expected result : 
        1. Test steps are equal in number to the expected
        2. Test step number mentioned either has or not has data
    
    """
    # if number_of_teststeps == None:
    #     number_of_teststeps = len(list(context.measurement_test_result))
    # # Test results are stored in the order - newest to oldest
    # measurement_test_result_list = list(context.measurement_test_result)
    # if (eval(result_exists) == True):
    #     assert number_of_teststeps >= 1, f"Unexpected. Vehicle generated {len(measurement_test_result_list)} steps which is less than {number_of_teststeps}"
    #     assert number_of_teststeps == len(measurement_test_result_list), f'Number of teststeps expected {number_of_teststeps} but found to be {len(measurement_test_result_list)} in number'
    # elif (eval(result_exists) == False):
    #     assert len(measurement_test_result_list) == 0, f"Unexpected. Vehicle generated {len(measurement_test_result_list)} steps when no test steps were expected"

    measurement_test_result_list = list(context.measurement_test_result)
    index_of_teststep_to_be_verified=len(measurement_test_result_list)-1
    if (eval(result_exists) == True):
        if (number_of_teststeps > 1):
            assert len(measurement_test_result_list) >= number_of_teststeps, f"Unexpected. Vehicle generated {len(measurement_test_result_list)} steps which is less than {number_of_teststeps}"
        else:
            assert len(measurement_test_result_list) == number_of_teststeps, f"Unexpected. Vehicle generated {len(measurement_test_result_list)} steps which is not equal to {number_of_teststeps}"
    elif (eval(result_exists) == False):
        assert len(context.measurement_test_result[measurement_test_result_list[index_of_teststep_to_be_verified]]['results']['data']) != 0, "Measurement data is completely blank even without headers"
        assert len(context.measurement_test_result[measurement_test_result_list[index_of_teststep_to_be_verified]]['results']['data']) == 1, "Unexpected. Vehicle generates Measurement Data when it was not supposed to"

@step('measurement test result for {number:d} numbereth step is "{available}"')
@step('measurement test result for latest step is "{available}"')
@step('measurement test result for latest step is available')
def step_impl(context, number = None, available = "available"):
    if number == None:
        number = len(list(context.measurement_test_result))
    # Test results are stored in the order - newest to oldest
    measurement_test_result_list = list(context.measurement_test_result)
    assert number <= len(measurement_test_result_list), f'Numbereth step asked for verification is {number}, but the total number of steps available are {len(measurement_test_result_list)}'
    logging.info(f'Validating the measurement result - {measurement_test_result_list[len(measurement_test_result_list) - number]}')
    index_of_teststep_to_be_verified = len(measurement_test_result_list) - number
    if available == 'available':
        assert len(context.measurement_test_result[measurement_test_result_list[index_of_teststep_to_be_verified]]['results']['data']) > 1, "Unexpected. Vehicle doesn't generate Measurement Data when it was supposed to"
    elif available == 'not available':
        assert len(context.measurement_test_result[measurement_test_result_list[index_of_teststep_to_be_verified]]['results']['data']) == 1, "Unexpected. Vehicle generates Measurement Data when it was not supposed to"
    logging.info('Measurement result validation successful!')

@step('measurement test step duration is validated with offset "{offset:d}"')
@step('measurement test step duration is validated')
def step_impl(context, offset = 25):
    """ Descirption : Validate the test step's duration from csv with the difference in time instances between the RM activation and deactivation
                        
    Pre-condition : 
        device "{device_id}" is mapped to vehicle "{vehicle_name}"
        measurement is activated
        measurement is recorded
        measurement is deactivated

    Parameters  :   NA
   
    Expected result : 
        1. Validation of duration is successful
    
    """
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    api_rm_obj.validate_teststep_duration(context.measurement_test_result, context.test_duration_ms_latest_measurement, offset)

@step('measurement data integrity test is performed for encoded measurement')
@step('measurement data integrity test is performed for the {number:d} numbereth test step of encoded measurement')
def step_impl(context, number = None):
    """ Descirption : Validate the measurement's data for the encoded signal
    Parameters  :   number - nth number of test step to be validated for data integrity. Latest teststep is number = latest and earliest teststep = 1                   
    Pre-condition : 
        device "{device_id}" is mapped to vehicle "{vehicle_name}"
        measurement is activated
        measurement test results are stored
        measurement is deactivated 
    """
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    measurement_test_result = context.measurement_test_result 

    if number != None:
        teststep_id = list(measurement_test_result.keys())[len(measurement_test_result) - number]
        teststep_result = measurement_test_result[teststep_id]
        single_test_result = json.loads(json.dumps({teststep_id:teststep_result}))
        measurement_test_result = single_test_result

    api_rm_obj.verify_encoded_signals_data(measurement_test_result,context.separation_time, table=context.table)


@step('measurement data integrity test is performed')
@step('measurement data integrity test is performed for calculated signals')
@step('measurement data integrity test is performed for calculated list signals')
@step('measurement data integrity test is performed for reused calculated signals')
@step('measurement data integrity test is performed for Multiplexed signals measurement')
@step('measurement data integrity test is performed for the {number:d} numbereth test step')
@step('measurement data integrity test is performed except for signals {signals}')
@step('measurement data integrity test is performed including configuration {version} validation')
def step_impl(context, number = None, signals = '', version = None): 
    """ Descirption : Validate the measurement's data according to its kind of signal/ signal combination
                        
    Pre-condition : 
        device "{device_id}" is mapped to vehicle "{vehicle_name}"
        measurement is activated
        measurement is recorded
        measurement is deactivated

    Parameters  :   number - nth number of test step to be validated for data integrity. Latest teststep is number = latest and earliest teststep = 1
                    signals - the signals which have to be excluded from data integrity validation
                    version - RM config version which will also be validated if it is not none
   
    Expected result : 
        1. Validation of signal(s) data is successful

    """
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    measurement_test_result = context.measurement_test_result 

    if signals != '':
        signals_to_be_excluded = signals.split(',')
        signals_to_be_excluded = [x.lower() for x in signals_to_be_excluded]
    else:
        signals_to_be_excluded = []

    if number != None:
        teststep_id = list(measurement_test_result.keys())[len(measurement_test_result) - number]
        teststep_result = measurement_test_result[teststep_id]
        single_test_result = json.loads(json.dumps({teststep_id:teststep_result}))
        measurement_test_result = single_test_result
    
    if version != None:
        version = context.measurement_configuration_version
    
    api_rm_obj.validate_measurement_data_integrity(measurement_test_result,context.separation_time, signals_to_be_excluded, measurement_configuration_version=version)
        
@step('measurement data integrity smoke test is performed')
def step_impl(context):
    """ Descirption : Validate the measurement's data according to its kind of signal/ signal combination for the first ten rows as SMOKE test
                        
    Pre-condition : 
        device "{device_id}" is mapped to vehicle "{vehicle_name}"
        measurement is activated
        measurement is recorded
        measurement is deactivated

    Parameters  :   NA
   
    Expected result : 
        1. Validation of signal(s) data is successful
    
    """
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    measurement_test_result = context.measurement_test_result

    api_rm_obj.validate_measurement_data_integrity(measurement_test_result,context.separation_time,signals_to_be_excluded=[],number_of_rows_to_validate=10)

@step('validate no new results are pushed to test step')
def step_impl(context):
    '''
            Descirption : Validates test step if any new results are pushed in upload cycles
            
            Pre-condition : measurement results are stored 
        
    '''
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    measurement_test_result = context.measurement_test_result
    for teststep_id in list(measurement_test_result.keys()):
        initial_recorded_duration, upload_interval = api_rm_obj.get_teststep_recorded_duration(teststep_id)
        wait_time = 2*int(upload_interval)
        logging.info(f"wait for next upload cycle {wait_time} seconds")
        time.sleep(wait_time)
        recorded_duration = api_rm_obj.get_teststep_recorded_duration(teststep_id)
        assert recorded_duration == initial_recorded_duration, f"data was not rejected by backend when vehicle and device has vin missmatch, recorded duration before missmatch {initial_recorded_duration} seconds and after missmatch {recorded_duration} seconds"
    
@step('validate the time difference between latest two RM test step results')
def step_impl(context):
    '''
            Descirption : Validates the duration between latest two RM test step results
            
            Pre-condition : Current measurment should be interpted by CL15/CL30
        
    '''
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    measurement_test_result = context.measurement_test_result
    list_of_keys = list(measurement_test_result.keys())
    last_index = len(list_of_keys)-1
    ''' Times from test Results '''
    second_last_result_end_time_obj = datetime.datetime.strptime(datetime.datetime.strptime(measurement_test_result[list_of_keys[last_index]]['end-time'],'%Y-%m-%dT%H:%M:%S.%fZ').strftime(context.std_date_format), context.std_date_format) 
    last_result_start_time_obj =  datetime.datetime.strptime(datetime.datetime.strptime(measurement_test_result[list_of_keys[last_index-1]]['start-time'],'%Y-%m-%dT%H:%M:%S.%fZ').strftime(context.std_date_format), context.std_date_format) 
    ''' Times from automation '''
    second_last_ref_end_time_obj =  datetime.datetime.strptime(datetime.datetime.strptime(str(context.device_offline_moment), '%Y-%m-%d %H:%M:%S.%f%z').strftime(context.std_date_format), context.std_date_format) 
    last_ref_start_time_obj =  datetime.datetime.strptime(datetime.datetime.strptime(str(context.device_online_moment), '%Y-%m-%d %H:%M:%S.%f%z').strftime(context.std_date_format), context.std_date_format) 
    ''' Converting time differnece into minutes'''
    ref_temp = str(last_ref_start_time_obj - second_last_ref_end_time_obj).split(':')
    res_temp = str(last_result_start_time_obj - second_last_result_end_time_obj).split(':')
    ''' duration in minuts '''
    ref_duration = (int(ref_temp[0]) *60 + int(ref_temp[1]))
    res_duration = (int(res_temp[0]) *60 + int(res_temp[1]))

    assert api_gen_obj.is_approximately_equal(ref_duration,res_duration,10),f"Results are not matching, Result duration : {res_duration} ->  Refrence duration : {ref_duration} "

@step('validate measurement data is recorded')
def step_impl(context):
    ''' Descirption : Validate the csv file contents for measurement record timings
                        
    Pre-condition : 
        device "{device_id}" is mapped to vehicle "{vehicle_name}"
        measurement is activated
        measurement is recorded

    Expected result : 
        1. Measurement results are available for the Vehicle
        2. Validation for the Record duration is successful
        3. Data in the CSV file should have recored data or No Data as per input time
    
    '''
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    delay = 0
    total_duration = context.test_duration/ 1000
    if(hasattr(context, 'start_trigger')) :
        trigger_json = context.start_trigger
        for trigger_ele in trigger_json['triggerElements']:
            if(trigger_ele['delay']> delay) : 
                delay = trigger_ele['delay']
    if(hasattr(context, 'measurement_end_time') and hasattr(context, 'end_time')) :
        total_duration += (context.end_time - context.measurement_end_time).total_seconds()
    exp_time = total_duration - delay;
    teststep_id = list(context.measurement_test_result.keys())[0]
    latest_result = context.measurement_test_result[teststep_id]
    if(exp_time > 0):
        try:
            act_time= api_rm_obj.get_recorded_time(latest_result)
            logging.info(f"Expected Duration = , {str(exp_time)}, and Actual Duration = , {str(act_time)}")
            assert abs(exp_time-act_time)<=100, "Difference between expected and Actual Record duration is more than 100 Seconds" 
        except TypeError: assert False, "Measurement doesn't contain any data in the CSV File"
    else:
        assert len(latest_result["results"]['data']) == 1, "Unexpected. Measurement Data is shown, Expected Data was empty"

@step('Remote measurement is activated')
@step('assign remote measurement to "{device_slot_name}" of vehicle "{vehicle_name}"')
@step('measurement configuration "{measurement_configuration_name}" is assigned')
def step_impl(context, device_slot_name = None, vehicle_name = None,  measurement_configuration_name = None):
    """
    Description: Assign the RM configuration to the Device slot of the specified Vehicle.
                Variables 
                start_time : Time when measurement activation is triggered
                measurement_start_time : Time when measurement is Active confirmed
                end_time : Time when measurement deactivation is triggered
                measurement_end_time : Time when measurement is Deactive confirmed

    Pre-condition : Vehicle is created and Device slot is available for the Vehicle, measurement confiugration is in released state
    
    Parameters  : 
        device_slot_name : name of the device slot where the measurmenent to be assigned.
            Default Value: None - When Device slot is choosen as None, the configuration will be assigned to the Contex.device_slot
        vehicle_name : name of the vehicle
            Default Value: None - When Device slot is choosen as None, the configuration will be assigned to Contex.vehicleName
        measurement_configuration_name: name of the measurement configuration, to be assigned in the vehicle
            Default Value: None - When Configuration name is selected as None. The configuration which is available at context.measurement_configuration_id will be selected.
   
    Expected result : Assignment is created successfully, and assignment Id is stored to context.all_assignment_jobs dictonary
    
    """   
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    start_time = datetime.datetime.now(datetime.timezone.utc)

    if context.device_slot_count =="" or context.meas_config_keys == [] or context.meas_config_keys == list(set(context.meas_config_keys).difference(set(context.measurement_configuration_list))):
        context.device_slot_count = 0
        
    if vehicle_name!=None:
        if(len(vehicle_name) == vehicle_name.count(' ')):
            vehicle_name = context.default_vehicle
        context.vehicle_name = vehicle_name
        context.vehicle_id =  api_fm_obj.get_vehicle_id_by_name(context.vehicle_name, context)
    if device_slot_name!=None:
        context.device_slot_name = device_slot_name + "_" + context.device_slot_type
    if measurement_configuration_name != None:
        context.measurement_configuration_id = api_rm_obj.get_measurement_configuration_id(measurement_configuration_name)
    context.measurement_configuration_version = api_rm_obj.get_measurement_configuration_version(context.measurement_configuration_id)
    api_rm_obj.trigger_measurement_assignment_activation(context.vehicle_id, context.device_slot_name, context.measurement_configuration_id)    
    logging.info(f"Measurement Configuration Assignment on, {context.vehicle_name}, vehicle, on device slot, {context.device_slot_name}, is SUCCESSFUL")
    time.sleep(10)
    assignment_details = api_rm_obj.get_measurement_assignment_details(context.vehicle_id, context.measurement_configuration_id, context.device_slot_name)
    context.assignment_job_id = assignment_details['mc2SlotAssignmentId']
    
    for measurement_configuration in context.measurement_configuration_list:
        if context.device_slot_count == 0:
            context.vehicle_data[context.vehicle_name]["remote_measurement"][measurement_configuration]={}
            context.meas_config_keys = list(context.vehicle_data[context.vehicle_name]["remote_measurement"].keys())
            context.device_slot_count = 1
    context.vehicle_data[context.vehicle_name]["remote_measurement"][measurement_configuration].update({"rm_job_id"+context.device_slot_name : context.assignment_job_id})
    context.all_assignment_jobs[context.assignment_job_id] = {'start_time': start_time, 'measurement_start_time': '', 'end_time': '', 'measurement_end_time': '', 'status': 'active'}
    if not hasattr(context, 'rm_activation_date') or context.rm_activation_date =="":
        rm_activation_date = str(start_time).split(".")
        context.rm_activation_date = datetime.datetime.strptime(rm_activation_date[0],"%Y-%m-%d %H:%M:%S")
        
@step('measurement status on vehicle "{vehicle_name}" device slot "{device_slot_name}" is "{exp_state}" with substatus "{substate}" and target status is "{target_status}"')
@step('measurement status on vehicle "{vehicle_name}" device slot "{device_slot_name}" is "{exp_state}" with target status as "{target_status}"')
@step('measurement status on campaign "{campaign_detail}" vehicle "{vehicle_name}" device slot "{device_slot_name}" is "{exp_state}" with substatus "{substate}" and target status is "{target_status}"')
@step('measurement status is "{exp_state}" within "{timer}" minutes')
@step('measurement status for configuration {measurement_config_name} is "{exp_state}" within "{timer}" minutes')
@step('measurement status is "{exp_state}"')
@step('measurement status "{exp_state}" and substatus "{substate}"')
@step('measurement status of vehicle "{vehicle_name}" is "{exp_state}" and substatus "{substate}"')
@step('measurement status of older version measurement configuration is "{exp_state}"')
def step_impl(context, exp_state, device_slot_name = None, vehicle_name = None, target_status = None, substate = None, timer = None, measurement_config_name = None, campaign_detail = None, count = None):
    """
    Descirption : To verify the measurement status of the measurement assignment on the perticular device slot of the vehicle, 
                    with the interval of 10 seconds for 10 minutes

    Pre-condition : Remote measurement is assigned to the Vehicle
    
    Parameters  : 
        vehicle_name : name of the vehicle, for which user should fetch RM details
        device_slot_name : name of the device slot
        exp_state: expected state of the measurement on the device slot
        target_status : target status of the measurement on the device slot
   
    Expected result : exp_state and target status are displayed as expected
    
    """   
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    measurement_config_id,assignment_job_id = None,None
    if vehicle_name is None:
        vehicle_name = context.vehicle_name
    elif (len(vehicle_name) == vehicle_name.count(' ')):
        vehicle_name = context.default_vehicle

    api_rm_obj.verify_rm_status_check(context, vehicle_name, device_slot_name, measurement_config_name, exp_state, substate, 
                                        target_status, timer, campaign_detail, measurement_config_id, assignment_job_id)
    
    all_jobs_inactive = True
    for assignment_job_id in context.all_assignment_jobs:
        if context.all_assignment_jobs[assignment_job_id]['status'] != 'inactive':
            all_jobs_inactive = False
            break

    if (exp_state == "INACTIVE") and all_jobs_inactive:
        context.rm_activation_status = False
                
@step('deactivate remote measurement "{measurement_configuration_name}" from "{device_slot_name}" of vehicle "{vehicle_name}"')
@step('Remote measurement is deactivated')
@step('Remote measurement "{measurement_configuration_name}" is deactivated') 
def step_impl(context, measurement_configuration_name=None, device_slot_name = None, vehicle_name = None):
    """
   Descirption :Deactivate the RM configuration to the Device slot of the specified Vehicle

    Pre-condition : vehicle has a RM in assigned state for the specified device slot
    
    Parameters  : 
        measurement_configuration_name: name of the measurement configuration
        device_slot_name : name of the device slot where the measurmenent to be assigned
        vehicle_name : name of the vehicle
   
    Expected result : Assignment deactivation is successfully triggered for the Vehicle
    
    """   
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    if vehicle_name!=None:
        if(len(vehicle_name) == vehicle_name.count(' ')):
            vehicle_name = context.default_vehicle
        context.vehicle_name = vehicle_name
        context.vehicle_id =  api_fm_obj.get_vehicle_id_by_name(context.vehicle_name, context)
    if measurement_configuration_name!=None:
        context.measurement_configuration_id = api_rm_obj.get_measurement_configuration_id(measurement_configuration_name)
    if device_slot_name!=None:
        context.device_slot_name = device_slot_name + "_" + context.device_slot_type
    assignment_details = api_rm_obj.get_measurement_assignment_details(context.vehicle_id, context.measurement_configuration_id,  context.device_slot_name)
    api_rm_obj.trigger_measurement_assignment_deactivation(context.vehicle_id, context.device_slot_name, assignment_details['mc2SlotAssignmentId'].strip())
    context.all_assignment_jobs[context.assignment_job_id]['end_time'] = datetime.datetime.now(datetime.timezone.utc)

@step('remote measurement "{measurement_configuration_name}" from "{device_slot_name}" of vehicle "{vehicle_name}" reactivation is triggered')
def step_impl(context, measurement_configuration_name, device_slot_name, vehicle_name):
    """
        Descirption :reactivate the RM configuration to the Device slot of the specified Vehicle
        Pre-condition : vehicle has a RM in assigned state for the specified device slot
        Parameters : 
                    measurement_configuration_name: name of the measurement configuration
                    device_slot_name : name of the device slot where the measurmenent to be assigned
                    vehicle_name : name of the vehicle
                    Expected result : Assignment reactivation is successfully triggered for the Vehicle
    """ 
    api_fm_obj = API_FleetManagement_Class.ApiFleetManagementClass(context.env, context.log_api_details)
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    if(len(vehicle_name) == vehicle_name.count(' ')):
            vehicle_name = context.default_vehicle
    context.vehicle_name = vehicle_name
    context.vehicle_id =  api_fm_obj.get_vehicle_id_by_name(context.vehicle_name, context)
    context.measurement_configuration_id = api_rm_obj.get_measurement_configuration_id(measurement_configuration_name)
    context.device_slot_name = device_slot_name + "_" + context.device_slot_type
    assignment_details = api_rm_obj.get_measurement_assignment_details(context.vehicle_id, context.measurement_configuration_id,  context.device_slot_name)
    rm_reactivation_response = api_rm_obj.trigger_measurement_assignment_reactivation(context.vehicle_id, context.device_slot_name, assignment_details['mc2SlotAssignmentId'].strip())
    if rm_reactivation_response:
        logging.info("Reactivation for vehicle has successfully activated")
    
@step('perform device mapping and unmaping from device slot "{number:d}" times on "{vehicle_name}" for remote measurement')
def step_impl(context, number, vehicle_name):
    
    """
    Description     : Load test for device mapping and unmamping when measurement is assigned
        
    Pre-condition   : Measurement configuration is assigned to the vehicle

    Parameters      :   number : number of times load test to be performed 
                        vehicle_name : Name of the Vehicle

    Expected result : Load test is successful and the results are verified
 
    
    """   
    context.repetitive_steps = f'''
                When measurement status on vehicle "{vehicle_name}" device slot "CCU1" is "ASSIGNED" with substatus "ASSIGNED" and target status is "ACTIVE"
                And map devices to device slot of "{vehicle_name}" vehicle
                    | slot_name | device	|
                    | CCU1     |  CCU 	|
                Then measurement status on vehicle "{vehicle_name}" device slot "CCU1" is "ACTIVE" with substatus "ACTIVATION_CONFIRMED" and target status is "ACTIVE"
                When reference system "MONonCAN" with Identifier "MONonCAN_500k_highloadidents" is started
                And test is executed for "3" minutes
                And reference system is stopped
                And VRS with protocol "MONonCAN" and identifier "MONonCAN_500k_highloadidents" is stopped
                Then unmap device "CCU" from vehicle
                And test is executed for "30" seconds
            '''
    context.execute_steps(f'''
        Given perform load test for {number} iterations with predefined steps
        When measurement test results are stored
        Then measurement test results are present and {number} in number
           ''')
       


@step('remote measurement deactivated for vehicle setup group')
@step('remote measurement is deactivated for vehicle setup group "{vsg_name}"')
def step_impl(context, vsg_name = None):
    """
   Descirption :Deactivate the RM configuration for Vehicle Setup Group

    Pre-condition : vehicle Setup Group has a RM in active state
   
    Expected result : Assignment deactivation is successfully triggered for the Vehicle Setup group
    
    """
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    if vsg_name is None:
        vsg_names=list(context.all_vsg_data.keys())
        for vsg_name in vsg_names:
            vsg_id=context.all_vsg_data[vsg_name]['vsg_id']
            slot_assignment_ids=context.all_vsg_data[vsg_name]['remote_measurements']['all_assignment_ids']
            vsg_device_slot = context.all_vsg_data[vsg_name]["device_slot"][0]
            context.vsg_rm_status = api_rm_obj.deactivate_vsg_rm_config(slot_assignment_ids, vsg_id, vsg_device_slot)
    else:
        vsg_id=context.all_vsg_data[vsg_name]['vsg_id']
        slot_assignment_ids=context.all_vsg_data[vsg_name]['remote_measurements']['all_assignment_ids']
        vsg_device_slot = context.all_vsg_data[vsg_name]["device_slot"][0]
        context.vsg_rm_status = api_rm_obj.deactivate_vsg_rm_config(slot_assignment_ids, vsg_id, vsg_device_slot)
    logging.info("Remote Measurement deactivated successfully in vehicle setup group")


@step('target status as "{exp_status}" for vehicle setup group is validated')
@step('target status as "{exp_status}" for vehicle setup group "{vsg_name}" is validated')
def step_impl(context, exp_status, vsg_name=None):
    """
    Description     : validate target status of RM config for vehicle setup group
        
    Pre-condition   : Measurement should be activated/deactivated for VSG

    Parameters      : exp_status : ACTIVE/INACTIVE

    Expected result : Target status of vsg must have the expected status

    """  
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    if vsg_name == None:
        vsg_id= context.vsg_id
    else:
        vsg_id=context.all_vsg_data[vsg_name]['vsg_id']
    for measurement_configuration in context.measurement_configuration_list:
        measurement_configuration_id = api_rm_obj.get_measurement_configuration_id(measurement_configuration)
        target_status=api_rm_obj.get_rm_vsg_target_status(exp_status, vsg_id, measurement_configuration_id, context.vsg_device_slot )
    logging.info(f'Target status is {target_status}')
    

@step('validate sync progress bar with "{exp_statistics}"')
@step('validate sync progress bar with "{exp_statistics}" for "{vsg_name}"')
def step_impl(context, exp_statistics, vsg_name=None):
    """
   Descirption : Target status of RM in vehicle Setup Group

    Pre-condition : RM for VSG should be activated or deactivated
    
    Parameters  : 
        exp_state : Expected target status after RM activation or deactivation
   
    Expected result : Target status of RM in Vehicle Setup group must have expected value
    
    """
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    context.json_data = api_gen_obj.parse_json_file(constantscampaign.CAMPAIGN_JSON_PATH)
    statistic_value = context.json_data[exp_statistics]["stats_validation"]

    if vsg_name == None:
        vsg_id= context.vsg_id
    else:
        vsg_id=context.all_vsg_data[vsg_name]['vsg_id']
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    for measurement_configuration in context.measurement_configuration_list:
        measurement_configuration_id = api_rm_obj.get_measurement_configuration_id(measurement_configuration)
        api_rm_obj.verify_status_sync_progress_for_vsg(statistic_value, vsg_id, measurement_configuration_id, context.vsg_device_slot)

@step('measurement data integrity smoke test is performed for vehicle setup group')
def step_impl(context):
    """
    Description     : Load test for device mapping and unmamping when measurement is assigned
        
    Pre-condition   : Measurement configuration is assigned to the vehicle

    Parameters      :   number : number of times load test to be performed 
                        vehicle_name : Name of the Vehicle

    Expected result : Load test is successful and the results are verified
 
    """
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    for vehicle in context.vehicle_data:
        measurement_test_result = context.vehicle_data[vehicle]["remote_measurement"]["rm_result"]
        api_rm_obj.validate_measurement_data_integrity(measurement_test_result,context.separation_time, signals_to_be_excluded=[], number_of_rows_to_validate=10)

@step('remote measurement is reactivated for vehicle setup group')
def step_impl(context):
    """
   Descirption : Reactivating RM in vehicle Setup Group

    Pre-condition : RM for VSG should be activated once and deactivated
   
    Expected result : Target status of RM in Vehicle Setup group must have expected value
    
    """
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)   
    for slot_assignment_id in context.slot_assignment_id:
        api_rm_obj.trigger_vsg_rm_reactivation(context.vsg_id, context.vsg_device_slot, slot_assignment_id)
    logging.info("Reactivation for vehicle setup group has successfully actiavted")

@step('measurement test step is verified with upload interval "{upload_interval:d}" for upload count "{upload_count:d}" cycles')
def step_impl(context, upload_interval, upload_count):

    """
    Description     : Verify measurements are uploaded to the backend after duration given in upload interval
        
    Pre-condition   : Measurement is activated

    Parameters      : upload_interval --> Upload interval, 
                      upload_count --> number of times the upload interval to be verified

    Expected result : Measurements are uploaded to the backend after the upload interval cycles
 
    """   
    
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    measurement_loaded = False
    upload_duration = 0
    offset = 0
    for measurement_duration in range(upload_interval, upload_interval * upload_count, upload_interval):
        time.sleep(upload_interval)
        start_time = time.time()
        measurement_loaded, upload_duration = api_rm_obj.verify_upload_interval(context, start_time, upload_interval, measurement_loaded, offset, upload_duration)

        if not measurement_loaded:
            logging.info(f"Timeout: Measurement not loaded in {upload_interval + upload_interval//2}seconds")
        assert abs(measurement_duration-upload_duration) < 3, f"upload interval mismatch, Expected duration: {measurement_duration}, Actual duration:{upload_duration}"
        logging.info(f"Expected measurement duration={measurement_duration}\nActual duration = {upload_duration}")

  
@step('"{measurement_phase}" of measurement details are requested returns "{status}"')
@step('"{measurement_phase}" of measurement details are requested')
@step('"{measurement_phase}" of measurement details are requested for "{all}" measurements')
def step_impl(context, measurement_phase,status="SUCCESS",all=None):
    """ 
    Descirption : Store test step id info 

        Pre-condition : 
        test results are verified

        test is executed for "{min}" minutes

        Remote measurement is activated

        Remote measurement is deactivated

    Parameters  :   measurement_phase : start reason or stop reason of measurement
   
    Expected result : 
        r: Boolean, true if a particular test has passed
    """  
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    results=context.measurement_test_result
    if hasattr(context,'trigger_json_data'):
        measurement_result=len(results)-1
    else:
        measurement_result = 0
    context.test_step_ids_info ={}
    # context.measurement_test_result has test step id info from new to old, so zero index hold new value.
    while measurement_result >= 0:
        if (len(results) > 1 and measurement_result==0 and hasattr(context,'trigger_json_data') and all==None):
            break
        teststep_id = list(results.keys())[measurement_result]
        logging.info(f"Fetching measurement reasons for test step id - {teststep_id}")
        test_step_id_info = api_rm_obj.get_test_step_id_info(teststep_id,measurement_phase,status)
        context.test_step_ids_info[teststep_id] = {'response' : test_step_id_info.json()}
        measurement_result-= 1
    

@step('validate "{expected_reasons}" reason as per trigger condition "{trigger_condition_name}"')
@step('validate "{expected_reasons}" as measurement reason')
def step_impl(context, expected_reasons, trigger_condition_name=None):
    """ 
    Descirption : Perform tests to verify the reason of measurement

        Pre-condition : 
        test results are verified

        test is executed for "{min}" minutes

        Remote measurement is activated

        Remote measurement is deactivated

    Parameters  :   trigger_condition_name : start reason or stop reason of measurement
                    expected_reason : expected start or stop reason
   
    Expected result : 
        r: Boolean, true if a particular test has passed
    
    """  
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    expected_reasons_list = expected_reasons.split(',')
    for expected_reason in expected_reasons_list:
        api_rm_obj.measurement_start_or_stop_reason_check(expected_reason,trigger_condition_name,context.test_step_ids_info)

@step('vehicle gps along with trip distance details are verified')
@step('gps along with trip distance details are verified for the geo positioning enabled duration')
@step('gps along with trip distance is verified for {trip}')
def step_impl(context, trip = None):
    """ 
    Descirption : This step verifies the GPS and GPS trip distance measurement details based on the vehicle Geo positioning status.
                  In case of a new trip the gps trip distance value starts from 0. For a normal measurement GPS tripdistance can start from any value.
                  GPS Scalar value validation is done by comparing the value in the GPS structure with the Scalars.

    Pre-condition : test results are stored

    Parameters  : trip: type of the trip
                        default value: None - In this case gps trip distance can start from any value as trip is in progress.
                        possible value: New Trip - In this case gps trip distance should start from 0
    Expected result : GPS trip distance and GPS Scalar values are verified as per GPS and trip status of vehicle.
    """  
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    if(trip != None and trip.upper() == 'NEW TRIP'):
        teststep_id = list(context.measurement_test_result.keys())[0]
        teststep_result = context.measurement_test_result[teststep_id]
        measurement_test_result = json.loads(json.dumps({teststep_id:teststep_result}))
        api_rm_obj.verify_gps_and_trip_distance(measurement_test_result,  context.geo_status, True)
    else:
        api_rm_obj.verify_gps_and_trip_distance(context.measurement_test_result,  context.geo_status)
    

@step('driver with driver_Id drives for {drive_time}minutes')
def step_impl(context, drive_time):
    for row in range(len(context.table.rows)):
        context.execute_steps(f'''
            When reference system "CANalization" with Identifier "{context.table.rows[row].cells[0]}_100ms" is started
        ''')

        context.execute_steps(f'''
            When test is executed for {drive_time} minutes
        ''')
        
        context.execute_steps(f'''
            When VRS with protocol "CANalization" and identifier "{context.table.rows[row].cells[0]}_100ms" is stopped
        ''')

@step('verify the drive time difference of driver change')
def step_impl(context):
    api_gen_obj = API_Generic_Class.ApiGenericClass()
    expected_driver_ids = [api_gen_obj.parse_json_file(constants.OTA_VEHICLE_DATA_DRIVER_ID_JSON_PATH)[row["driver_Id"]] for row in context.table]
    measurement_results = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details).get_measurement_results(context.vehicle_id, context.rm_activation_date)
    measurement_data = measurement_results[list(measurement_results.keys())[0]]["results"]["data"]
    driver_id_index =  0
    for i in range(1, len(measurement_data) - 1):
        if measurement_data[i]["DI"] != expected_driver_ids[driver_id_index] and measurement_data[i]['Driver1Identification'] == None and measurement_data[i]['Driver2Identification'] == None :
            if driver_id_index < len(expected_driver_ids) - 1:
                driver_id_index+=1
            assert measurement_data[i]["DI"] == expected_driver_ids[driver_id_index], f"Driver ids mismatch, Expected driver id:{expected_driver_ids[driver_id_index]}, Actual driver id:{measurement_data[i]['DI']}"
            time_diff_of_drivers = float(measurement_data[i]['time_relative']) - float(measurement_data[i-1]['time_relative'])
            assert time_diff_of_drivers < 22.0, f"Time difference between driver switch is more than the limit, Expected limit: 22.0, Actual: {time_diff_of_drivers}"
         
            
@step('verify "{num_of_samples:d}" samples are present for all signals')
@step('verify "{num_of_samples:d}" samples are present for "{signal_name}" signals')
def step_impl(context, num_of_samples, signal_name = None):
    """
    Description : Checks number of samples present in the measurement CSV for each signal
    Pre-condition : measurement test results are stored
    
    Parameters  : 
        num_of_samples : Number of data samples per signal 
                        Eg: 5
        signal_name : Name of the signal
                      Default Value: None: Selects all signals in the measurement configuration
                      Eg: "SupplyVoltage,Signal_05"
                      
    Expected result : Data samples are present for the signal as mentioned
    """
    
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    signal_list = []
    if(signal_name == None):
        signal_details = api_rm_obj.get_measure_config_signals(context.measurement_configuration_id)
        for signal in signal_details:
            signal_list.append(signal["signalName"])
    else:
        signal_list = signal_name.split(",")
    api_rm_obj.verify_number_of_samples(context.measurement_test_result, signal_list, num_of_samples)

@step('validate preview data for the measurement configuration "{measurement_configuration_name}"')
@step('validate "{calculated_signal}" matrix for the measurement configuration "{measurement_configuration_name}" in preview data')
def step_impl(context, measurement_configuration_name,calculated_signal=None):
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    measurement_configuration_id = api_rm_obj.get_measurement_configuration_id(measurement_configuration_name)
    if calculated_signal != None:
        api_rm_obj.validate_calculated_preview_data(context.measurement_test_result,calculated_signal)
    else:
        api_rm_obj.validate_preview_data(context.measurement_test_result, measurement_configuration_id)

@step('measurement data integrity smoke test is performed for RM campaign')
def step_impl(context):
    """
    Description     : Load test for device mapping and unmamping when measurement is assigned
        
    Pre-condition   : Measurement configuration is assigned to the vehicle

    Parameters      :   number : number of times load test to be performed 
                        vehicle_name : Name of the Vehicle

    Expected result : Load test is successful and the results are verified
 
    """
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    for vehicle in context.vehicle_data:
        vehicle_id = context.vehicle_data[vehicle]["vehicle_id"]
        for campaign_id in context.activation_campaign_ids:
            if vehicle_id in context.campaign_vehicle_data[campaign_id]["vehicle_ids"]:
                measurement_test_result = context.vehicle_data[vehicle]["remote_measurement"]["rm_result"+campaign_id+vehicle_id]
                api_rm_obj.validate_measurement_data_integrity(measurement_test_result,context.separation_time, signals_to_be_excluded=[], number_of_rows_to_validate=10)

@step('check "{expected_state}" measurement configuration in "{vsg_name}" and generate logs if active measurement configuration found')
def step_impl(context,vsg_name, expected_state):

    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    vsg_id=vsg_id=context.all_vsg_data[vsg_name]['vsg_id']
    actual_state=api_rm_obj.check_measurement_configuration_status(vsg_id, vsg_name)
    if expected_state != actual_state:
        context.execute_steps('''
            Given device log count is fetched
            when triggering new log file generation for device
            Then "1" new log entries are generated for the device
     ''')
        assert False,f'Active RM configurations found in VSG or Vehilces which is not expected,Please find the timestamp {context.log_time_stamp} to download logs'

@step('validate data for "{signals_to_check}" for measurement configuration "{configuration_name}"')
def step_impl(context, signals_to_check, configuration_name):

    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    
    signals_list = signals_to_check.split(",")
    expected_test_step=False
    
    for teststep_id in list(context.measurement_test_result.keys()):
        measurement_configuration_id_from_teststep = api_rm_obj.get_measurement_config_id_from_teststep_id(teststep_id)
        measurement_configuration_id_from_config_name = api_rm_obj.get_measurement_configuration_id(configuration_name)
        if measurement_configuration_id_from_teststep == measurement_configuration_id_from_config_name:
            expected_test_step=True
            context.test_step_id=teststep_id
            result = context.measurement_test_result[teststep_id]
            data_array = result['results']['data']
            assert len(data_array) > 1, "No data in the measurement, measurement data is empty"
            rows_to_validate = len(data_array)-1
            for signal in signals_list:
                signal_name = signal.split(':')[0]
                signal_value = signal.split(':')[1]
                api_rm_obj.validate_data_for_signals(rows_to_validate,signal_name,signal_value,data_array)
            break
    assert expected_test_step == True,f'The test step for {configuration_name} is not generated'    

@step('validate preview data for VTripDuration for the measurement configuration')
def step_impl(context):

    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    try:
        api_rm_obj.prepare_preview(context.test_step_id)
    except Exception as e:
        logging.info(f"The prepare preview is already triggered for the test step id {context.test_step_id} with error:{e}")
    finally:
        measurement_test_result=api_rm_obj._get_preview_data(context.test_step_id)

    value_in_range = False
    actual_message_and_signal_count = len(measurement_test_result["_embedded"]["series"])
    for i in range(actual_message_and_signal_count):   
        if measurement_test_result["_embedded"]["series"][i]['seriesName']=='VTripDuration':
            data_value=measurement_test_result["_embedded"]["series"][i]["dataPoints"][0]["value"]['ndArray']
            actual_value=data_value[0]
            if(float(actual_value) >=920.5 and float(actual_value) <= 924.5):
                logging.info("The data of VTripDuration is in expected range")
                value_in_range=True
                break   
    assert value_in_range == True,f'The actual value {actual_value} is not in the expected range between 881.77 to 1281.77'


@step('verify "{trigger}" as per "{triggercondition}" for "{trigger_phases}",create if not present')
@step('verify "{trigger}" as per "{triggercondition}" for "{trigger_phases}" with "{pre_post_trigger_values}" seconds,create if not present')
def step_impl(context, trigger, triggercondition, trigger_phases, pre_post_trigger_values = None):
    """
    Description     : It checks the existing trigger conditions in measurement config, if exisiting trigger conditions are as expected
                      it ignores adding the triggers again, else it calls the (Add Expected trigger "{trigger}" conditions) step and add expected triggers
        
    Pre-condition   : Measurement config should have triggers should compare, if not it will directly add expected triggers

    Parameters      :   trigger:E2E_Test_Trigger in trigger.json
                        triggercondition : expected trigger condition from trigger.json
                        trigger_phases : start and stop trigger
                        pre_post_trigger_values : preTrigger and postTrigger seconds
                        
                        
    Expected result : if exisitng trigger condtions matches it skips adding triggers, else add the expected trigger conditions
 
    """
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    api_gen_obj = API_Generic_Class.ApiGenericClass()

    pre_post_trigger_values_dict = {"preTrigger":0,"postTrigger":None}

    if pre_post_trigger_values is not None:
        updated_trigger_values = json.loads(pre_post_trigger_values)
        pre_post_trigger_values_dict.update(updated_trigger_values)

    context.trigger_phase_list=trigger_phases.split(',')
    context.expected_data_dict = {"basic_data":None,"startTrigger":None,"stopTrigger":None}
    actual_data_dict = {"basic_data":None,"startTrigger":None,"stopTrigger":None}

    trigger_json_data = api_gen_obj.parse_json_file(constants.RM_TRIGGER_JSON)
    basic_trigger_data = trigger_json_data["trigger"][trigger.lower()]
    
    context.pre_trigger,context.post_trigger,expected_basic_data = api_rm_obj.update_data_with_pre_post_trigger_time(pre_post_trigger_values_dict['preTrigger'],pre_post_trigger_values_dict['postTrigger'],basic_trigger_data)
    context.expected_data_dict["basic_data"]=expected_basic_data

    for phase in context.trigger_phase_list:
        data = trigger_json_data["triggerTestData"][triggercondition][phase]
        trigger_data = api_rm_obj.prepare_expected_trigger_data(context.measurement_configuration_id, data)
        context.expected_data_dict[phase]=trigger_data
    
    trigger_id = api_rm_obj.get_trigger_id_of_mc(context.measurement_configuration_id)

    if trigger_id!=None:
        actual_basic_data = api_rm_obj.get_trigger_info_of_mc(context.measurement_configuration_id)
        actual_data_dict["basic_data"]=actual_basic_data

        actual_data_dict["startTrigger"] = api_rm_obj.check_and_get_trigger_data(context.measurement_configuration_id, trigger_id, "startTrigger")
        actual_data_dict["stopTrigger"] = api_rm_obj.check_and_get_trigger_data(context.measurement_configuration_id, trigger_id, "stopTrigger")

        for key in context.expected_data_dict.keys():
            trigger_data_matching = api_rm_obj.compare_trigger_data(actual_data_dict[key],context.expected_data_dict[key])
            if trigger_data_matching == False:
                logging.info(f'The Existing {key} trigger conditions are not matching with expected, Hence adding the expected {key} conditions..')
                context.execute_steps(f'''
                    Given Add Expected trigger "{trigger}" conditions"        
                ''')
                break
            logging.info(f'The existing {key} trigger conditions matches with exepcted conditions..')
    else:
        logging.info(f'There is no Existing trigger in measurement configuration {context.measurement_configuration_name} , Hence adding the expected trigger conditions..')
        context.execute_steps(f'''
            Given Add Expected trigger "{trigger}" conditions"        
        ''')
        
@step('Add Expected trigger "{trigger}" conditions"')
def step_imp(context, trigger):

    """
    Description     : It adds the expected trigger conditions in measurement configuration
        
    Pre-condition   : Measurement configuration should be available

    Parameters      : trigger: trigger datas from trigger.json,measurement_configuration_name
                        
    Expected result : The expected trigger conditions should be addedd in measurement configuration

    """

    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)

    context.execute_steps(f'''
        Given Measurement job "{context.measurement_configuration_name}" is in "draft" state
        And Attempt to "Delete" trigger "{trigger}" returns "Success"        
    ''')

    context.trigger_id = api_rm_obj.add_trigger(context.measurement_configuration_id, context.expected_data_dict["basic_data"])

    context.execute_steps(f'''
        Given verify trigger "{trigger}" is "Add"ed successfully        
    ''')

    for phase in context.trigger_phase_list:
        api_rm_obj.add_expected_start_stop_trigger_conditions(context, phase, context.expected_data_dict[phase])
        
        context.execute_steps(f'''
            Then verify trigger condition "{phase}" is "Add"ed successfully
        ''')
    
    context.execute_steps(f'''
        Given Attempt to "Activate" trigger "{trigger}"
        Then Verify Measurement job "{context.measurement_configuration_name}" can be set to "Release" state
    ''')
    
@step('re-activate remote measurement for "{count:d}" times using retry option')
@step('re-deactivate remote measurement for "{count:d}" times using retry option')
def step_impl(context, count):
    api_rm_obj = API_OTA_Vehicle_Data_Class.ApiOTAVehicleDataClass(context.env, context.log_api_details)
    measurement_job_id = api_rm_obj.get_latest_measurement_job_id(context.vehicle_id,context.device_slot_name)
    api_rm_obj.retry_rm_activation_deactivation(count, context.vehicle_id, measurement_job_id)

@step('"{command}" and "{action}" remote measurement')
def step_impl(context, command, action):
    context.execute_steps(f'''
        When command to "{command}" GSM mode of the device
        Then wait for device to be "OFFLINE"
     ''')
    if action == 'activate':
        context.execute_steps('''
            When Remote measurement is activated
            Then measurement status "INACTIVE" and substatus "IN_ACTIVATION"
        ''')
    else:
        context.execute_steps('''
            When Remote measurement is deactivated
            Then measurement status "ACTIVE" and substatus "IN_DEACTIVATION"
        ''')
              
