import schedule
import time
import logging
import sys
from functools import partial
from MQTT import Publisher, Subscriber, Client, PublisherAdapter
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

dht11 = DHT11(17) # dht11 on gpio 17
dht11.run()


dht11_temperature = PublisherAdapter("/sensors/dht11/01/temperature", dht11.get_temperature)
dht11_humidity = PublisherAdapter("/sensors/dht11/01/humidity", dht11.get_humidity)
rpi_cpu_temp = RPiSensors.CPUTemperature("/sensors/temperature/cpu")
rpi_gpio_pump1 = RPiSensors.GPIO("/devices/pump/air", 27, True, GPIO.OUT, False)
rpi_gpio_pump2 = RPiSensors.GPIO("/devices/pump/circulation", 22, False, GPIO.OUT, True)
temp_tank = I2CDevices.ADS1115_NTC_ChannelAdapter("/sensors/temperature/tank", ads_ntc, 1)
temp_ext = I2CDevices.ADS1115_NTC_ChannelAdapter("/sensors/temperature/ext", ads_ntc, 2)


paho_mqtt_client = MQTTClient.Client()
paho_mqtt_client.username_pw_set("hydro01", "password")


mqtt_client = Client(paho_mqtt_client, "hydro01")

# first add sensors and actors
mqtt_client.add(dht11_temperature)
mqtt_client.add(dht11_humidity)
mqtt_client.add(rpi_cpu_temp)
mqtt_client.add(rpi_gpio_pump1)
mqtt_client.add(rpi_gpio_pump2)
mqtt_client.add(temp_tank)
mqtt_client.add(temp_ext)

# finally connect
mqtt_client.connect("localhost")

schedule.every(60).seconds.do(exec_threaded, dht11_temperature.publish)
schedule.every(60).seconds.do(exec_threaded, dht11_humidity.publish)
schedule.every(60).seconds.do(exec_threaded, rpi_cpu_temp.publish)
schedule.every(60).seconds.do(exec_threaded, rpi_gpio_pump1.publish)
schedule.every(60).seconds.do(exec_threaded, rpi_gpio_pump2.publish)
schedule.every(60).seconds.do(exec_threaded, temp_tank.publish)
schedule.every(60).seconds.do(exec_threaded, temp_ext.publish)


while True:
    schedule.run_pending()
    time.sleep(1)
