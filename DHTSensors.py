from MQTT import Publisher, Subscriber, Client
import Adafruit_DHT
import threading
import time
import log
import Threaded
import Filter

class DHT11(Threaded.Threaded):
    def __init__(self, gpio : int):
        self.logger = log.get_logger("DHT11")
        super(DHT11, self).__init__(self.logger)

        self.delay = 2 # at least 2 seconds between measurements for DHT11!
        self.gpio = gpio
        self.humidity = None
        self.temperature = None
        self.humidity_filter = Filter.MovingAverage(10, True, 10., 2)
        self.temperature_filter = Filter.MovingAverage(10, True, 10., 2)
        self.lock = threading.Lock()

    def looped(self):
        with self.lock:
            humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, self.gpio)
            self.humidity = self.humidity_filter.feed(humidity)
            self.temperature = self.temperature_filter.feed(temperature)

        time.sleep(self.delay)

    def get_temperature(self):
        with self.lock:
            return self.temperature

    def get_humidity(self):
        with self.lock:
            return self.humidity



