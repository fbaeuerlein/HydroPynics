from MQTT import Publisher, Subscriber, Client
import Adafruit_ADS1x15
import math
import smbus
import threading
import time
import log

class ADS1115_NTC(object):
    def __init__(self):
        self.r_serial = 22e3    # 22kOhm
        self.address = 0x48     # I2C address
        self.gain = 1               # voltage range gain level
        self.max_voltage = 4.096    # resulting voltage range 
        self.coeffs = [8.00796252e-04,  2.80177169e-04, -3.14619144e-06, 3.06728618e-07]
        self.ref_channel = 3    # channel that measures the ref voltage
        self.temperatures_per_channel = []
        self.adc =Adafruit_ADS1x15.ADS1115(address=self.address, )
        self.measurements = 5 # number of measurements to do
        self.measurement_delay = 5000 # delay between measurements in ms
        self.lock = threading.Lock()
        self.logger = log.get_logger("ADS1115")


    def __to_volt__(self, value : int):
        return self.max_voltage * value / 32768.

    def __get_voltage__(self, channel : int):
        return self.__to_volt__(self.adc.read_adc(channel, gain=self.gain))

    def __temperature_from_volt__(self, u_ntc : float, u_ref : float):
        r = 22000
        u_r = abs(u_ref - u_ntc)
        i = u_r / r
        r_ntc = u_ntc / i

        log_r = math.log(r_ntc)
        sum = 0.
        for i in range(0, len(self.coeffs)):
            sum += self.coeffs[i] * math.pow(log_r, i)

        return ( 1. / sum ) - 273.15 # kelvin to °C

    # get the reference channel voltage
    def __get_ref_voltage__(self):
        return self.__get_voltage__(self.ref_channel)

    def __get_temperature__(self, channel : int):
        u_ref = self.__get_ref_voltage__()
        u_channel = self.__get_voltage__(channel)

        # if we have not connected or shorted channel,
        # channel and ref voltage could be the same
        if u_ref <= u_channel: return -273.15
        return self.__temperature_from_volt__(u_channel, u_ref)

    # reads the temperature of all channels
    def __acquire_temperature__(self):

        temperatures = []
        for channel in range(0, 3):
            t = 0
            for _ in range(0, self.measurements):
                t += self.__get_temperature__(channel)
                time.sleep(self.measurement_delay / 1000.)
                
            t /= float(self.measurements)
            temperatures.append(t)
        
        with self.lock:
            self.temperatures_per_channel = temperatures


    def __thread_loop__(self):
        while True:
            self.__acquire_temperature__()
            time.sleep(10)

    def run(self):
        self.logger.info("Starting thread for ADS1115")
        threading.Thread(target=self.__thread_loop__).start()


    def get_channel_temperature(self, channel : int):
        with self.lock:
            # not filled already?
            if len(self.temperatures_per_channel) <= channel:
                raise "Not ready yet"
            return self.temperatures_per_channel[channel]

'''
    Adapter class to get temperature from specific channel
'''
class ADS1115_NTC_ChannelAdapter(Publisher):
    def __init__(self, topic_base : str, ads_ntc : ADS1115_NTC, channel : int):
        super(ADS1115_NTC_ChannelAdapter, self).__init__(topic_base)        
        self.ads_ntc = ads_ntc
        self.channel = channel

    def get_value(self):
        return { "value" : round(self.ads_ntc.get_channel_temperature(self.channel), 1) }
