import threading
import logging

'''
Small abstraction for thread loops
'''
class Threaded(object):
    def __init__(self, logger : logging.Logger):
        self.__stop__ = threading.Event()
        self.__stop__.set() # not running from the start
        self.__stopped__ = threading.Event()
        self.logger = logger
        self.thread = None

    def running(self): 
        return not self.__stop__.is_set()

    def __thread_loop__(self):
        self.logger.info("Thread started.")
        while self.running():
            try:
                self.looped()
            except Exception as e:
                self.logger.warn("Exception in looped(): {}".format(e))

        self.__stopped__.set()

    def looped(self):
        pass

    def run(self):
        if self.running(): 
            self.logger.warn("Thread already running!")
            return

        self.__stop__.clear()
        self.__stopped__.clear()
        self.logger.info("Starting thread.")
        self.thread = threading.Thread(target=self.__thread_loop__)
        self.thread.start()    

    def stop(self):
        if not self.running():
            self.logger.warn("Thread already stopped!")
            return

        self.logger.info("Stopping thread.")
        self.__stop__.set()
        self.thread.join()
        self.logger.info("Thread stopped.")

            