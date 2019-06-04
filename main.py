import schedule
import time
import json
import logging
import sys
from functools import partial
from MQTT import Publisher, Subscriber, Client

class Switch(Publisher, Subscriber):
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

class Temperature(Publisher):
    def __init__(self, topic_base : str):
        super(Temperature, self).__init__(topic_base)
        self.value = 20

    def get_value(self):
        return self.value

switch = Switch("/switch/fan/01")
sensor = Temperature("/sensor/temperature/01")
# actor = Actor("/switch/fan/02")


mqtt_client = Client()

# first add sensors and actors
mqtt_client.add(switch)
mqtt_client.add(sensor)

# finally connect
mqtt_client.connect("localhost")

schedule.every(5).seconds.do(switch.publish)
schedule.every(10).seconds.do(sensor.publish)

while True:
    schedule.run_pending()
    time.sleep(5)
