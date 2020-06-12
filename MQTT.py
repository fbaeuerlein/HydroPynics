
import paho.mqtt.client as MQTTClient
import json
import log
import sys

logger = log.get_logger("MQTT")     

class NamedBase(object):
    def __init__(self, name):
        self.name = name
   

class Publisher(NamedBase):
    def __init__(self, topic : str):
        self.pub_topic = topic + "/state"
        self.topic = topic
        self.client = None
        super(Publisher, self).__init__(topic)

    def get_value(self):
        return None

    def publish(self):

        # if client is not already set, do nothing
        if self.client is None:
            logger.warn("No client set. Failed to publish!")
            pass

        try:
            payload = self.get_value()
        except: 
            logger.warn("Failed to get value for '{}'.".format(self.topic))
            payload = None

        ''' 
            provide a common message scheme 
            {
                "id" : "device_id",
                "payload" : { "value" : XXX },
                "measurement" : "_topic_tree_replaced_slash_with_underscore"
            }
        '''
        measurement = self.topic.replace('/', '_')
        message = { "id" : self.client.device_id(), "payload" : payload, "measurement" : measurement }
        self.client.mqtt_client().publish(self.topic, payload=json.dumps(message))
        self.report_state(message)
    
    def report_state(self, value):
        logger.info("[{}] State: '{}'".format(self.topic, value))    

''' adapter to call a getter function from elsewhere and publishing it's value '''
class PublisherAdapter(Publisher):
    def __init__(self, topic_base : str, getter):
        super(PublisherAdapter, self).__init__(topic_base)
        self.getter = getter

    def get_value(self):
        return { "value" : self.getter() }

class Subscriber(NamedBase):
    def __init__(self, topic):
        super(Subscriber, self).__init__(topic)
        self.sub_topic = topic + "/set"

    def set_value(self, value):
        pass
    
    def on_message(self, client, userdata, message):
        try:
            msg = message.payload.decode('utf-8')
            logger.info("[{}] received: '{}'".format(self.sub_topic, msg))
            self.set_value(json.loads(msg)["value"])
        except Exception as e:
            logger.warning("Failed to decode/parse message: {}".format(e))
            logger.warning('Message: {}'.format(msg))

    def subscribe(self, client : MQTTClient.Client):
        logger.info("Subscribing for topic '{}'".format(self.sub_topic))
        client.subscribe(self.sub_topic)
        client.message_callback_add(self.sub_topic, self.on_message)    

    def unsubscribe(self, client : MQTTClient.Client):
        client.mqtt_client().unsubscribe(self.sub_topic)

class Client(object):
    def __init__(self, device_id : str, debug : bool = True):
        self.client = MQTTClient.Client()
        self.client.enable_logger(log.get_logger("PAHO"))
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.device_id_ = device_id
        self.items = []

    def device_id(self):
        return self.device_id_

    def mqtt_client(self):
        return self.client

    def connect(self, mqtt_host, mqtt_port : int = 1883):
        self.client.connect(mqtt_host, port=mqtt_port)
        self.client.loop_start()
        logger.info("Connected '{}' to '{}'".format(self.device_id_, mqtt_host))

    def username_pw_set(self, username : str, password : str):
        self.client.username_pw_set(username, password)

    def add(self, item):
        # set client to publisher/subscriber
        item.client = self
        self.items.append(item)

    def on_connect(self, client, userdata, flags, rc):
        logger.info("Connected!")
        for i in self.items:
            # just Subscribers can subscribe for changes
            if isinstance(i, Subscriber):
                i.subscribe(client)

    def on_disconnect(self, client, userdata, rc):
        logger.info("Disconnected!")
        for i in self.items:
            if isinstance(i, Subscriber):
                i.unsubscribe(self)

    def on_message(self, client, userdata, message):
        logger.info("Unhandled message received: {}".format(message.payload))
