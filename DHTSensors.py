from MQTT import Publisher, Subscriber, Client
import Adafruit_DHT

class DHT11(Publisher):
    def __init__(self, topic_base : str, gpio : int):
        super(DHT11, self).__init__(topic_base)
        self.gpio = gpio
        self.value = {}

    def get_value(self):
        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, self.gpio)
        return { "humidity" : { "value" : humidity }, "temperature" : { "value" : temperature } }