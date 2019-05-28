import schedule
import time
import paho.mqtt.client as MQTTClient
import json
import logging
import sys
from functools import partial
from SensorActor import Sensor, SensorActor, Actor

class Switch(SensorActor):
    '''
    Simple fake switch implementation
    '''
    def __init__(self, topic_base : str):
        super(Switch, self).__init__(topic_base)
        self.value = False

    def get_value(self):
        return self.value

    def set_value(self, value):
        self.value = value

switch = Switch("/switch/fan/01")
sensor = Sensor("/sensor/temperature/01")
actor = Actor("/switch/fan/02")

class Daemon(object):
    def __init__(self):
        self.client = MQTTClient.Client()
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect
        self.items = []

    def connect(self, mqtt_host = "localhost"):
        self.client.connect(mqtt_host)
        self.client.loop_start()

    def add(self, item):
        item.client = self.client
        self.items.append(item)

    def on_connect(self, client, userdata, flags, rc):
        for i in self.items:
            # just actors can subscribe for changes
            if isinstance(i, Actor):
                i.subscribe(client)

    def on_disconnect(self, client, userdata, rc):
        print("Disconnected!")

    def on_message(self, client, userdata, message):
        print("Unhandled message received: {}".format(message.payload))


daemon = Daemon()
daemon.connect("localhost")
daemon.add(switch)
daemon.add(sensor)
daemon.add(actor)

schedule.every(5).seconds.do(switch.publish)
schedule.every(15).seconds.do(sensor.publish)

while True:
    schedule.run_pending()
    time.sleep(5)


#class Sensor(object):
#     def __init__(self, topic : str, default_value = None):
#         self.pub_topic = topic + "/state"
#         self.value = default_value

#         self.logger = logging.getLogger(topic)
#         self.logger.setLevel(logging.INFO)
#         self.logger_handler = logging.StreamHandler(stream=sys.stdout)
#         self.logger_handler.setFormatter(logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s '))
#         self.logger.addHandler(self.logger_handler)
#         #self.logger.info("Setting up sensor: '{}' '{}'".format(self.pub_topic, self.sub_topic))        

#     def get_value(self):
#         return { "value" : self.value }

#     def publish(self, client):
#         client.publish(self.pub_topic, payload=json.dumps(self.get_value()))
    
#     def report_state(self):
#         self.logger.info("State: '{}'".format(self.get_value()))    

# class Actor(object):
#     def __init__(self, topic_base : str, default_value = None):
#         super(Switch, self).__init__(topic_base, default_value=default_value)
#         self.sub_topic = topic_base + "/set"

# class Switch(Sensor):
#     def __init__(self, topic_base : str, default_value = None):
#         super(Switch, self).__init__(topic_base, default_value=default_value)
#         self.sub_topic = topic_base + "/set"

#     def on_message(self, client, userdata, message):
#         try:
#             msg = message.payload.decode('utf-8')
#             self.value = json.loads(msg)["value"]
#         except Exception as e:
#             self.logger.warning("Failed to parse message: {}".format(e))
#             self.logger.warning('Message: {}'.format(msg))

#     def subscribe(self, client):
#         client.subscribe(self.sub_topic)
#         client.message_callback_add(self.sub_topic, self.on_message)


