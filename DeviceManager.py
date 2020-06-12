import schedule
import time
import log
import MQTT 
import threading

def exec_threaded(f):
    threading.Thread(target=f).start()

class DeviceManager(object):
    def __init__(self, client : MQTT.Client):
        self.logger = log.get_logger("DEVMGR")
        self.client = client

    def add(self, device : object, interval : int, threaded : bool = True):
        if isinstance(device, MQTT.Publisher):
            if threaded:
                schedule.every(interval).seconds.do(exec_threaded, device.publish)
            else:
                schedule.every(interval).seconds.do(device.publish)
        self.client.add(device)

    def run(self):
        while True:
            schedule.run_pending()
            time.sleep(1)

