import time
import socks
import ssl
from paho.mqtt.client import Client
from src.common.message_processor import MessageProcessor
from src.common import constants
from src.common.logger import get_logger
log = get_logger()
class MqttPlugin:
    def __init__(self, device_id):
        self.client_id = device_id
        self.client = Client(self.client_id)
        self.client.on_connect = self.__on_connect
        self.client.on_disconnect = self.__on_disconnect
        self.client.on_log = self.__on_log
        self.client.on_message = self.__on_message
        self.device_running = False
  
    def __on_connect(self, client: Client, userdata, flags, rc):
        """ 
            MQTT - on-connect callback function, automatically called when connect is requested
        """
        if rc == 0:
            log.info(f"Device {self.client_id} connected to backend successfully")
            self.device_running = True
            self._subscribe()
        else:
            log.error(f"Failed to connect {self.client_id}, return code: {rc}")
    
    def __on_disconnect(self, client: Client, userdata, rc):
        """ 
           MQTT - on-disconnect callback function, automatically called when disconnect is requested
        """
        if rc == 0:
            log.debug("Disconnection from backend is successful")
            self.device_running = False
        else:
            log.debug("Failed to disconnect, return code %d\n", rc)

    def __on_log(self, client: Client, userdata, level, buf):
        """ 
            MQTT - on-log callback function,automatically called when there is logging needed
        """
        log.debug("MQTT Log: "+buf)

    def __on_message(self, client, userdata, message):
        """ 
            MQTT - on-message callback function, when a publish message is received this function will be called
        """
        log.debug(f"Received Publish on Topic: '{message.topic}'")
        log.debug(f"Received Message: '{message.payload}'")
        topic_name = message.topic.rsplit('/',1)[1]
        publish_data = self.process_message.process_incoming_message(topic_name, message.payload)
        if len(publish_data)>0:
            self.publish_message(publish_data)

    def _connect(self, device_data, env_details, **kwargs):
        """
            connect method will invoke a MQTT connection based on the provided device and environment details.
            MQTT Client will be started and the client will try to connect to the backend

        Args:
            device_data (dictionary): Details of the device including certificate path and VIN
            env_details (dictionary): Details of the environment
            kwargs (known arguments):
                                        vin (string): VIN data for vehicle
                                        proxy_address (string): Proxy address for backend connection
                                        proxy_port (string): Proxy port for backend connection
                                        csv_path (string): path to signal/message data csv file
            """
        env_data = env_details[device_data['environment']]
        proxy = None
        if(kwargs['proxy_address'] != None):
            self.client.proxy_set(proxy_type=socks.HTTP, proxy_addr = kwargs['proxy_address'] , proxy_port = kwargs['proxy_port'])
            proxy = kwargs['proxy_address'] + ":" + str(kwargs['proxy_port'])
        elif env_data['proxy_required'] == True:
            self.client.proxy_set(proxy_type=socks.HTTP, proxy_addr=env_data['proxy_address'], proxy_port=env_data['proxy_port'])
            proxy = env_data['proxy_address'] + ":" + str(env_data['proxy_port'])
        self.client.tls_set(ca_certs = device_data['ca_path'],certfile=device_data['cert_path'],keyfile=device_data['key_path'],cert_reqs =ssl.CERT_NONE, tls_version=ssl.PROTOCOL_TLSv1_2)
        self.client.tls_insecure_set(True)
        log.debug(f"Connecting to MQTT Endpoint- {env_data['mqtt_url']}:{env_data['port_no']}")
        self.client.connect(env_data['mqtt_url'], env_data['port_no'])
        self.client.loop_start()
        self.process_message = MessageProcessor(self.client_id,device_data['cert_path'], device_data['key_path'], kwargs['vin'], kwargs['csv_path'], proxy)

    def _subscribe(self, qos = 1):
        """
            This method will register the subscription to the topics which are stored in constants.SUBSCRIBE_TOPICS

        Args:
            qos (int, optional): Quality of service . Defaults to 1. Allowed values are (0,1,2)
        """
        topic_list = [(topic.format(device_id =self.client_id),qos) for topic in constants.SUBSCRIBE_TOPICS]
        self.client.subscribe(topic_list, qos)

    def _publish(self, topic_name, message):
        """
            This method will publish the message to the backend on the requested topic

        Args:
            topic_name (String): name of the topic, to which message should be published
            message (serialized protobuf message): Serialized protobuf message which should be published to the topic
        """
        topic = topic_name.format(device_id =self.client_id)
        result = self.client.publish(topic, message)
        status = result[0]
        if status == 0:
            log.debug(f"Sent `{message}` to topic `{topic}`")
        else:
            log.error(f"Failed to send message to topic {topic}")

    def publish_message(self, message_data):
        """
            Iterates through message data dictionary and tries to publish to the backend
        Args:
            message_data (dictionary): Message data dictionary, that contains topic name as key and message to be published as data.
        """
        for topic_name, result_protobuf in message_data.items():
            if(topic_name != None):
                if isinstance(result_protobuf, list):
                    for result in result_protobuf:
                        self._publish(topic_name, result)
                else:
                    self._publish(topic_name, result_protobuf)
    
    def run_device(self, device_data, env_details, **kwargs):
        """
            This method will invoke connect and then it will subscribe to the specific topics
        Args:
            device_data (dictionary): Details of the device including certificate path and VIN
            env_details (dictionary): Details of the environment
            kwargs (known arguments):
                                        vin (string): VIN data for vehicle
                                        proxy_address (string): Proxy address for backend connection
                                        proxy_port (string): Proxy port for backend connection
                                        csv_path (string): path to signal/message data csv file
        Returns:
            start_success(bool): Success state of the connection
            
        """
        log.info(f"Sending connection request for Device: {self.client_id}")
        start_success = False
        self._connect(device_data, env_details, **kwargs)
        for seconds in range(45):
            if self.device_running == True:
                start_success = True
                break
            time.sleep(1)
            if(seconds == 44):
                log.error("Device was not able to connect to backend after waiting for 45 seconds")
        return start_success


    def send_messages(self, message_type = None, **kwargs):
        """
            This method will fetch the data which should be published to the backend.
            If the data is available to send to backend, it will be published else it will be skipped
        Args:
            message_type (String, optional):Type of the message, currently supported values ("MEASUREMENT,GPS,VIN") 
                                            Default - None (Fetches Measurement and GPS result by default)
            kwargs (known arguments):       Optional known arguments
                                            vin - for vin VIN data
                                            duration - GPS measurement duration
                                            geo_data - GEO data calculated as per requirement
                                            
                                         
        """
        publish_data = self.process_message.prepare_outgoing_messages(message_type, **kwargs)
        if len(publish_data)>0:
            self.publish_message(publish_data)
        
    
    def stop_device(self):
        """
            Disconnects the connection from Backend
        """
        self.client.loop_stop()
        self.client.disconnect()
        log.info(f"Device: {self.client_id} stopped successfully")