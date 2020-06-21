import RPi.GPIO as GPIO 
import time
import Filter
import Threaded
import log
import threading


# GPIO_TRIGGER = 13
# GPIO_ECHO = 19

class HCSR04(Threaded.Threaded):
	def __init__(self, trigger_pin : int, echo_pin : int, max_response_time : int = 6., **kwargs ):
		if "max_response_time" in kwargs:
			self.max_response_time = kwargs["max_response_time"]
		else:
			self.max_response_time = 6. # ms

		self.logger = log.get_logger("HCSR04")
		super(HCSR04, self).__init__(self.logger)
		self.delay_between_samples = 250 # in ms
		self.gpio_trigger = trigger_pin
		self.gpio_echo = echo_pin
		self.max_response_time = max_response_time
		GPIO.setup(self.gpio_trigger, GPIO.OUT)
		GPIO.setup(self.gpio_echo, GPIO.IN)
		GPIO.output(self.gpio_trigger, False)
		self.filter = Filter.MovingAverage(25, True, 20.)
		self.travel_time = None
		self.lock = threading.Lock()
		  
	def __velocity__(self, temperature : float = 20.):
		"""Returns the temperature compensated velocity in air
		see https://en.wikipedia.org/wiki/Speed_of_sound#Dependence_on_the_properties_of_the_medium

		Args:
			temperature (float, optional): Temperature of air in °C. Defaults to 20.

		Returns:
			float: Velocity in air in m/s
		"""
		return 331.3 + 0.606 * temperature

	def looped(self):
		"""called repeatedly by the thread and does the measurement
		"""

		# keep trigger high for at least 10us
		GPIO.output(self.gpio_trigger, True)
		time.sleep(0.00006)
		GPIO.output(self.gpio_trigger, False)

		# use monotonic clock to avoid time changes
		start = stop = time.monotonic()
		
		# actively wait for echo!
		while GPIO.input(self.gpio_echo) == 0:
			start = time.monotonic()
		while GPIO.input(self.gpio_echo) == 1 and (stop - start) * 1000. < self.max_response_time:
			stop = time.monotonic()
		if (stop - start) * 1000. > self.max_response_time:
			self.logger.info("Echo came to late!")
			time.sleep(self.delay_between_samples / 1000)
			return
			
		elapsed = stop - start
		oneway_travel_time = elapsed / 2
		
		with self.lock: 
			self.travel_time = self.filter.feed(oneway_travel_time)
		
		time.sleep(self.delay_between_samples / 1000)


	def get_distance(self, temperature : float = 20.): 
		"""Returns the measured distance with temperature compensation

		Args:
			temperature (float, optional): Current air temperature in °C. Defaults to 20.

		Returns:
			float : current measured distance
			None : if nothing measured 
		"""
		with self.lock:
			travel_time = self.travel_time

		if travel_time is None:
			return None

		return travel_time * self.__velocity__(temperature)

