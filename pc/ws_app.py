# from gensim.models import Word2Vec
from tornado import websocket, web, ioloop
from datetime import datetime as dt
from apis.text_tone_analyzer import ToneAnalyzer
from apis.geocoder_ip import get_robot_location
from awareness import RobotAwareness

import json
import os
import time


cl = []
# MODELS_DIR = 'models/'
# model_gs = Word2Vec.load(os.path.join(MODELS_DIR, 'text8_gs.bin'))


class SocketHandler(websocket.WebSocketHandler):

    def __init__(self):
        self.ta = ToneAnalyzer()
        self.robotAwareness = RobotAwareness(self)

    def check_origin(self, origin):
        return True

    def open(self):
        if self not in cl:
            cl.append(self)
            print(str(len(cl)) + ' connected...')

    def on_message(self, message):
        print("receive " + message)

        robot_experience = json.loads(message)
        robot_experience['emotionalState'] = list(self.ta.get_tone_from_text(robot_experience['speech']).values())
        robot_experience['datetime'] = dt.now()
        robot_experience['place'] = get_robot_location()

        self.robotAwareness.interpret_robot_experience(robot_experience)

        # send_message = {}
        # send_message['data'] = 'I have received message'
        # self.command_robot_speak(send_message)

    def on_close(self):
        if self in cl:
            cl.remove(self)
            print('1 disconnected...')

    def command_robot_speak(self, message):
        """ encode dictionary message command to json and forward to robot """
        for conn in cl:
            conn.write_message(json.dumps(message))


class ApiHandler(web.RequestHandler):

    @web.asynchronous
    def get(self, *args):
        id = self.get_argument("id")
        value = self.get_argument("value")
        data = {"id": id, "value": value}
        data = json.dumps(data)
        self.write(data)
        self.finish()

    @web.asynchronous
    def post(self):
        self.write(json.dumps({'success': True}))
        self.finish()

app = web.Application([
    (r'/ws', SocketHandler),
    (r'/api', ApiHandler),
    (r'/(.*)', web.StaticFileHandler, {'path': os.getcwd()})
])


if __name__ == '__main__':
    print("server listening on port 8888")
    app.listen(8888)
    ioloop.IOLoop.instance().start()
