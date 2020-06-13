from MQTT import Publisher, Subscriber, Client
import math
import threading
import time
import log
import Filter
import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import Threaded

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

class ADS1115(object):
    def __init__(self, gain : int = 1, ref_channel : int = None):
        self.ads = ADS.ADS1115(i2c)
        self.ads.gain = gain # see datasheet for gain levels (defines voltage range)
        chans = [ADS.P0, ADS.P1, ADS.P2, ADS.P3 ] # available channels
        self.channels = []
        self.ref_channel = ref_channel

        # if no ref channel selected, just use the channels as they are
        if ref_channel is None: 
            for chan in chans:
                self.channels.append(AnalogIn(self.ads, chan))
        else:
            if ref_channel < 0 or ref_channel > 3:
                raise ValueError("invalid reference channel")
            
            for chan in chans:
                if chan == chans[ref_channel]: continue # omit ref channel
                # might throw if wrong combination is selected
                self.channels.append(AnalogIn(self.ads, chan, chans[ref_channel]))
            
    def ref(self): 
        return self.ref_channel

    def __check_channel_index__(self, channel : int):
        if channel < 0 or channel > 3:
            raise ValueError("invalid channel number")        
        if not self.ref_channel is None:
            if self.ref_channel == channel:
                raise ValueError("can't select ref channel")

    def get_value(self, channel : int):
        self.__check_channel_index__(channel)
        return self.channels[channel].value

    def get_voltage(self, channel : int):
        self.__check_channel_index__(channel)
        return self.channels[channel].voltage

'''
    Vcc -----------+----------------------------+
                   |                            |
                  [ ] R_serial                  |
                   |                            |
                   +----------------+         U_ref
                   |                |           |
                  [ ] R_NTC        U_NTC        |
                   |                |           |
    GND -----------+----------------+-----------+
'''
class NTCAdapter(object):
    def __init__(self, ads : ADS1115, channel : int, ref_channel : int):
        self.ads = ads
        self.channel = channel
        self.ref_channel = ref_channel

        self.r_serial = 22e3    # 22kOhm
        self.coeffs = [8.00796252e-04,  2.80177169e-04, -3.14619144e-06, 3.06728618e-07]

    def get_temperature(self):
        # vcc to gnd
        u_ref = self.ads.get_voltage(self.ref_channel)

        # voltage of ntc (ntc to ground)
        u_ntc = self.ads.get_voltage(self.channel)

        # resulting voltage at the measurment resistor
        u_r = abs(u_ref - u_ntc)

        # current through the measurement resitor
        i = u_r / self.r_serial

        # resulting resistance of the ntc
        r_ntc = u_ntc / i

        # use Steinhart-Hart-Equation for temperature estimation
        log_r = math.log(r_ntc)
        sum = 0.
        for i in range(0, len(self.coeffs)):
            sum += self.coeffs[i] * math.pow(log_r, i)

        return ( 1. / sum ) - 273.15 # kelvin to °C

class ADSTemperatureThreadedReader(Threaded.Threaded):
    def __init__(self, adapters : [NTCAdapter]):

        self.logger = log.get_logger("ADSReader")
        super(ADSTemperatureThreadedReader, self).__init__(self.logger)

        self.adapters = adapters
        self.measurements = 5 # number of measurements to do
        self.measurement_delay = 1000 # delay between measurements in ms
        self.filters = []
        for _ in range(0, len(self.adapters)):
            self.filters.append(Filter.MovingAverage(10))
        self.temperatures = [None] * len(self.adapters)
        self.lock = threading.Lock()


    # reads the temperature of all channels
    def looped(self):
        temperatures = [0] * len(self.adapters)

        for i in range(0, len(self.adapters)):
            temperatures[i] = self.filters[i].feed(self.adapters[i].get_temperature())

        with self.lock:
            self.temperatures = temperatures

        time.sleep(self.measurement_delay / 1000.)

    def get_channel_temperature(self, channel : int):
        if channel < 0 or channel >= len(self.adapters):
            raise ValueError("invalid channel number '{}'".format(channel))

        with self.lock:
            value = self.temperatures[channel]

        if value is None: 
            return None
        else:
            return round(value, 1)

# class ADS1115_NTC(object):
#     def __init__(self):
#         self.r_serial = 22e3    # 22kOhm
#         self.address = 0x48     # I2C address
#         self.gain = 1               # voltage range gain level
#         self.max_voltage = 4.096    # resulting voltage range 
#         self.coeffs = [8.00796252e-04,  2.80177169e-04, -3.14619144e-06, 3.06728618e-07]
#         self.ref_channel = 3    # channel that measures the ref voltage
#         self.temperatures_per_channel = []
#         self.adc =Adafruit_ADS1x15.ADS1115(address=self.address, )
#         self.measurements = 5 # number of measurements to do
#         self.measurement_delay = 5000 # delay between measurements in ms
#         self.lock = threading.Lock()
#         self.logger = log.get_logger("ADS1115")


#     def __to_volt__(self, value : int):
#         return self.max_voltage * value / 32768.

#     def __get_voltage__(self, channel : int):
#         return self.__to_volt__(self.adc.read_adc(channel, gain=self.gain))

#     def __temperature_from_volt__(self, u_ntc : float, u_ref : float):
#         r = 22000
#         u_r = abs(u_ref - u_ntc)
#         i = u_r / r
#         r_ntc = u_ntc / i

#         log_r = math.log(r_ntc)
#         sum = 0.
#         for i in range(0, len(self.coeffs)):
#             sum += self.coeffs[i] * math.pow(log_r, i)

#         return ( 1. / sum ) - 273.15 # kelvin to °C

#     # get the reference channel voltage
#     def __get_ref_voltage__(self):
#         return self.__get_voltage__(self.ref_channel)

#     def __get_temperature__(self, channel : int):
#         u_ref = self.__get_ref_voltage__()
#         u_channel = self.__get_voltage__(channel)

#         # if we have not connected or shorted channel,
#         # channel and ref voltage could be the same
#         if u_ref <= u_channel: return -273.15
#         return self.__temperature_from_volt__(u_channel, u_ref)

#     # reads the temperature of all channels
#     def __acquire_temperature__(self):

#         temperatures = []
#         for channel in range(0, 3):
#             t = 0
#             for _ in range(0, self.measurements):
#                 t += self.__get_temperature__(channel)
#                 time.sleep(self.measurement_delay / 1000.)
                
#             t /= float(self.measurements)
#             temperatures.append(t)
        
#         with self.lock:
#             self.temperatures_per_channel = temperatures


#     def __thread_loop__(self):
#         while True:
#             self.__acquire_temperature__()
#             time.sleep(10)

#     def run(self):
#         self.logger.info("Starting thread for ADS1115")
#         threading.Thread(target=self.__thread_loop__).start()


#     def get_channel_temperature(self, channel : int):
#         with self.lock:
#             # not filled already?
#             if len(self.temperatures_per_channel) <= channel:
#                 raise "Not ready yet"
#             return self.temperatures_per_channel[channel]

