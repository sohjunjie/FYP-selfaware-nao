from threading import Thread
import time


class Reaction(Thread):

    def __init__(self, awareness, wsApp):
        super().__init__()
        self.awareness = awareness
        self.wsApp = wsApp

    def speak(self, speech):
        send_message = {}
        send_message['data'] = speech
        self.wsApp.command_robot_speak(send_message)

    def start(self):
        self.running = True
        super().start()

    def run(self):
        self.idle()

    def stop(self):
        self.running = False

    def idle(self):
        while(self.running):
            time.sleep(0.2)
