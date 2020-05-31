from MQTT import Publisher, Subscriber, Client
import Adafruit_ADS1x15
import math
import smbus
import threading
import time

'''
    direction: True = output, False = input
'''
class PCF8574T(Publisher, Subscriber):
    def __init__(self, topic_base : str, address :int, channel : int, inverted : bool, direction : bool):
        super(PCF8574T, self).__init__(topic_base)
        self.address = address
        self.channel = channel
        self.bus = smbus.SMBus(bus=1)
        self.inverted = inverted
        self.direction = direction
        self.value = int(0)

    def value_for_channel(self, data):
        result =  data & ( 0x01 << self.channel ) != 0
        if self.inverted: 
            return not result
        else:
            return result

    def get_value(self):
        if self. direction: 
            data = self.value
        else:
            data = self.bus.read_byte(self.address)
        return self.value_for_channel(data)

    def set_value(self, value):

        if self.inverted:
            requested_value = not value
        else:
            requested_value = value
        mask = 0x01 << self.channel

        current = self.bus.read_byte(self.address)
        state = current & mask != 0

        new_value = current

        if state :
            if not requested_value: 
                new_value = ~mask & current
                self.bus.write_byte_data(self.address, 0x00, new_value)

        else:
            if requested_value: 
                new_value = mask | current
                self.bus.write_byte_data(self.address, 0x00, new_value)


class ADS1115_NTC(object):
    def __init__(self):
        self.r_serial = 22e3    # 22kOhm
        self.address = 0x48     # I2C address
        self.gain = 1
        self.max_voltage = 4.096
        self.coeffs = [8.00796252e-04,  2.80177169e-04, -3.14619144e-06, 3.06728618e-07]
        self.ref_channel = 3    # channel that measures the ref voltage
        self.temperatures_per_channel = []
        self.adc =Adafruit_ADS1x15.ADS1115(address=self.address, )


    def to_volt(self, value : int):
        return self.max_voltage * value / 32768.

    def get_voltage(self, channel : int):
        return self.to_volt(self.adc.read_adc(channel, gain=self.gain))

    def temperature_from_volt(self, u_ntc : float, u_ref : float):
        r = 22000
        u_r = abs(u_ref - u_ntc)
        i = u_r / r
        r_ntc = u_ntc / i

        log_r = math.log(r_ntc)
        sum = 0.
        for i in range(0, len(self.coeffs)):
            sum += self.coeffs[i] * math.pow(log_r, i)

        return ( 1. / sum ) - 273.15

    def get_ref_voltage(self):
        return self.get_voltage(self.ref_channel)

    def get_temperature(self, channel : int):
        u_ref = self.get_ref_voltage()
        u_channel = self.get_voltage(channel)

        # if we have not connected or shorted channel,
        # channel and ref voltage could be the same
        if u_ref == u_channel: return -273.15
        return self.temperature_from_volt(u_channel, u_ref)

    def _acquire_temperature(self):

        temperatures = []
        for channel in range(0, 3):
            t = 0
            for _ in range(0, 5):
                t += self.get_temperature(channel)
            t /= 5.
            temperatures.append(t)
        
        self.temperatures_per_channel = temperatures


    def _thread_loop(self):
        while True:
            self._acquire_temperature()
            time.sleep(10)

    def run(self):
        print("Starting thread for ADS1115")
        threading.Thread(target=self._thread_loop).start()


    def get_channel_temperature(self, channel : int):
        if len(self.temperatures_per_channel) <= channel:
            raise "Not ready yet"
        return self.temperatures_per_channel[channel]

class ADS1115_NTC_ChannelAdapter(Publisher):
    def __init__(self, topic_base : str, ads_ntc : ADS1115_NTC, channel : int):
        super(ADS1115_NTC_ChannelAdapter, self).__init__(topic_base)        
        self.ads_ntc = ads_ntc
        self.channel = channel

    def get_value(self):
        return { "value" : round(self.ads_ntc.get_channel_temperature(self.channel), 1) }
