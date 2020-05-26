
import paho.mqtt.client as MQTTClient
import json
import logging
import sys

logger = logging.getLogger("MQTT")
logger.setLevel(logging.INFO)
logger_handler = logging.StreamHandler(stream=sys.stdout)
logger_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s %(name)-12s %(message)s '))
logger.addHandler(logger_handler)     

class NamedBase(object):
    def __init__(self, name):
        self.name = name
   

class Publisher(NamedBase):
    def __init__(self, topic : str):
        self.pub_topic = topic + "/state"
        super(Publisher, self).__init__(topic)
        self.client = None

    def get_value(self):
        pass
        #return { "value" : self.value }

    def publish(self):
        if self.client is None:
            pass
        self.client.publish(self.pub_topic, payload=json.dumps(self.get_value()))
        self.report_state()
    
    def report_state(self):
        logger.info("[{}] State: '{}'".format(self.pub_topic, self.get_value()))    

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
        client.subscribe(self.sub_topic)
        client.message_callback_add(self.sub_topic, self.on_message)    

class Client(object):
    def __init__(self):
        self.client = MQTTClient.Client()
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.items = []

    def connect(self, mqtt_host = "localhost"):
        self.client.connect(mqtt_host)
        self.client.loop_start()
        logger.info("Connected to '{}'".format(mqtt_host))

    def add(self, item):
        item.client = self.client
        self.items.append(item)

    def on_connect(self, client, userdata, flags, rc):
        for i in self.items:
            # just actors can subscribe for changes
            if isinstance(i, Subscriber):
                i.subscribe(client)

    def on_disconnect(self, client, userdata, rc):
        logger.info("Disconnected!")

    def on_message(self, client, userdata, message):
        logger.info("Unhandled message received: {}".format(message.payload))
