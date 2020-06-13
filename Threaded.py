import threading
import logging

'''
Small abstraction for thread loops
'''
class Threaded(object):
    def __init__(self, logger : logging.Logger):
        self.__stop__ = threading.Event()
        self.__stop__.set() # not running from the start
        self.logger = logger

    def running(self): 
        return not self.__stop__.is_set()

    def __thread_loop__(self):
        self.logger.info("Thread started.")
        while self.running():
            self.looped()
        self.logger.info("Thread stopped.")

    def looped(self):
        pass

    def run(self):
        if self.running(): 
            self.logger.warn("Thread already running!")
            return

        self.__stop__.clear()
        self.logger.info("Starting thread.")
        threading.Thread(target=self.__thread_loop__).start()    

    def stop(self):
        if not self.running():
            self.logger.warn("Thread already stopped!")
            return

        self.logger.info("Stopping thread.")
        self.__stop__.set()
            