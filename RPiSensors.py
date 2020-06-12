from subprocess import PIPE, Popen
from MQTT import Publisher, Subscriber, Client
import RPi.GPIO


class CPUTemperature(Publisher):
    def __init__(self, topic_base : str):
        super(CPUTemperature, self).__init__(topic_base)

    def get_value(self):
        process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
        out, error = process.communicate()
        output = out.decode('utf-8')
        temperature = float(output[output.index('=') + 1:output.rindex("'")])
        return { "value" : temperature }

class GPIO(Publisher, Subscriber):
    '''
    Simple implementation for RPi GPIO
    mode = True is out, false is in
    '''
    def __init__(self, topic_base : str, pin : int, initial_value : bool, mode, inverted : bool = False  ):
        super(GPIO, self).__init__(topic_base)
        self.value = initial_value
        self.pin = pin
        self.inverted = inverted
        RPi.GPIO.setup(pin, mode)
        self.__set_value(initial_value)   

    def get_value(self):
        result = bool(RPi.GPIO.input(self.pin))

        # convert to int (if using bool, telegraf will not convert it currently)
        if self.inverted:
            return { "value" : int(not result) }
        else:
            return { "value" : int(result) }

    def set_value(self, value):
        self.__set_value(value)
        super(GPIO, self).publish() # publish immediately after set

    def __set_value(self, value):
        if self.inverted:
            RPi.GPIO.output(self.pin, not value)
        else:
            RPi.GPIO.output(self.pin, value)
