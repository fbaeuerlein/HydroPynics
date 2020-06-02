import schedule
import time
import logging
import sys
from functools import partial
from MQTT import Publisher, Subscriber, Client
import paho.mqtt.client as MQTTClient

from DHTSensors import DHT11
import RPiSensors
import threading
import RPi.GPIO as GPIO
import I2CDevices

GPIO.setmode(GPIO.BCM)

def exec_threaded(f):
    threading.Thread(target=f).start()

#
ads_ntc = I2CDevices.ADS1115_NTC()
ads_ntc.run()

dht11 = DHT11("/sensors/temperature/dht", 17)
rpi_cpu_temp = RPiSensors.CPUTemperature("/sensors/temperature/cpu")
rpi_gpio_pump1 = RPiSensors.GPIO("/devices/pump/air", 27, True, GPIO.OUT, False)
rpi_gpio_pump2 = RPiSensors.GPIO("/devices/pump/circulation", 22, False, GPIO.OUT, True)
temp_tank = I2CDevices.ADS1115_NTC_ChannelAdapter("/sensors/temperature/tank", ads_ntc, 1)

paho_mqtt_client = MQTTClient.Client()
paho_mqtt_client.username_pw_set("hydro01", "secret")


mqtt_client = Client(paho_mqtt_client)

# first add sensors and actors
mqtt_client.add(dht11)
mqtt_client.add(rpi_cpu_temp)
mqtt_client.add(rpi_gpio_pump1)
mqtt_client.add(rpi_gpio_pump2)
mqtt_client.add(temp_tank)

# finally connect
mqtt_client.connect("192.168.178.23")

schedule.every(10).seconds.do(exec_threaded, dht11.publish)
schedule.every(1).seconds.do(exec_threaded, rpi_cpu_temp.publish)
schedule.every(1).seconds.do(exec_threaded, rpi_gpio_pump1.publish)
schedule.every(1).seconds.do(exec_threaded, rpi_gpio_pump2.publish)
schedule.every(5).seconds.do(exec_threaded, temp_tank.publish)

while True:
    schedule.run_pending()
    time.sleep(5)
