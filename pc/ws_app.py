# from gensim.models import Word2Vec
from tornado import websocket, web, ioloop
from datetime import datetime as dt
from apis.text_tone_analyzer import ToneAnalyzer
from apis.geocoder_ip import get_robot_location
from awareness import RobotAwareness
import json
import logging
import os
import time

logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%d-%m-%Y:%H:%M:%S',
                    level=logging.INFO)

cl = []


class SocketHandler(websocket.WebSocketHandler):

    def __init__(self, application, request, **kwargs):
        super(SocketHandler, self).__init__(application, request, **kwargs)
        self.ta = ToneAnalyzer()
        self.robotAwareness = RobotAwareness(self)

        print("")
        print("")
        print("")
        print("")
        print("==========Initialized==========")

    def check_origin(self, origin):
        return True

    def open(self):
        if self not in cl:
            cl.append(self)
            print(str(len(cl)) + ' connected...')

    def on_message(self, message):
        robot_experience = json.loads(message)
        robot_experience['emotionalState'] = list(self.ta.get_tone_from_text(robot_experience['speech']).values())
        robot_experience['datetime'] = dt.now()
        robot_experience['place'] = get_robot_location()

        logging.info("Awareness Websocket: Received data from Nao")
        logging.info("Awareness Websocket: Constructing Robot Experience = " + str(robot_experience))
        logging.info("Awareness Websocket: Sending Robot Experience to perception...")

        self.robotAwareness.interpret_robot_experience(robot_experience)

    def on_close(self):
        if self in cl:
            cl.remove(self)
            print('1 disconnected...')
        self.robotAwareness.exeProc.dialogueManager.reset()

    def command_robot_speak(self, message):
        """ encode dictionary message command to json and forward to robot """
        logging.info("Awareness Websocket: Received speak command from reaction")
        logging.info("Awareness Websocket: Writing response to Nao")
        for conn in cl:
            conn.write_message(json.dumps(message))


app = web.Application([
    (r'/ws', SocketHandler),
])


if __name__ == '__main__':
    print("server listening on port 8888")
    app.listen(8888)
    ioloop.IOLoop.instance().start()
