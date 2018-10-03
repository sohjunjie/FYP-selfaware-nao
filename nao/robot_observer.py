from config import logging
import threading
import time


class RobotObserver(threading.Thread):
    def __init__(self):
        super(RobotObserver, self).__init__()
        logging.info("Robot observer thread initialized")

    def start(self):
        self.running = True
        super(RobotObserver, self).start()

    def run(self):
        while(self.running):
            time.sleep(5)
            self.observe()

    def stop(self):
        self.running = False

    def observe(self):
        logging.info('I am observing every 5 secs')
