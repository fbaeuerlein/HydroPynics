import schedule
import time
import paho.mqtt.client as MQTTClient
import json
import logging
import sys
from functools import partial



class NamedBase(object):
    def __init__(self, name):
        self.name = name
        self.logger = logging.getLogger("{}".format(name))
        self.logger.setLevel(logging.INFO)
        self.logger_handler = logging.StreamHandler(stream=sys.stdout)
        self.logger_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s %(name)-12s %(message)s '))
        self.logger.addHandler(self.logger_handler)        

class Sensor(NamedBase):
    def __init__(self, topic : str):
        self.pub_topic = topic + "/state"
        super(Sensor, self).__init__(topic)

    def get_value(self):
        pass
        #return { "value" : self.value }

    def publish(self, client : MQTTClient.Client ):
        
        client.publish(self.pub_topic, payload=json.dumps(self.get_value()))
    
    def report_state(self):
        self.logger.info("State: '{}'".format(self.get_value()))    

class Actor(NamedBase):
    def __init__(self, topic):
        super(Actor, self).__init__(topic)
        self.sub_topic = topic + "/set"

    def set_value(self, value):
        pass
    
    def on_message(self, client, userdata, message):
        try:
            msg = message.payload.decode('utf-8')
            self.logger.info("received: '{}'".format(msg))
            self.set_value(json.loads(msg)["value"])
        except Exception as e:
            self.logger.warning("Failed to decode/parse message: {}".format(e))
            self.logger.warning('Message: {}'.format(msg))

    def subscribe(self, client : MQTTClient.Client):
        client.subscribe(self.sub_topic)
        client.message_callback_add(self.sub_topic, self.on_message)    

class SensorActor(Sensor, Actor):
    def __init__(self, topic_base : str, default_value = None):
        super(SensorActor, self).__init__(topic_base)
        self.sub_topic = topic_base + "/set"


