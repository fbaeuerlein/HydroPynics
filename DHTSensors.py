from MQTT import Publisher, Subscriber, Client
import Adafruit_DHT
import threading
import time

class DHT11(object):
    def __init__(self, gpio : int):
        self.delay = 10
        self.gpio = gpio
        self.humidity = None
        self.temperature = None
        self.lock = threading.Lock()
        pass

    def __acquire_data__(self):
        with self.lock:
            self.humidity, self.temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, self.gpio)
        

    def __thread_loop__(self):
        while True:
            self.__acquire_data__()
            time.sleep(self.delay)

    def get_temperature(self):
        with self.lock:
            return self.temperature

    def get_humidity(self):
        with self.lock:
            return self.humidity

    def run(self):
        print("Starting thread for DHT11")
        threading.Thread(target=self.__thread_loop__).start()


