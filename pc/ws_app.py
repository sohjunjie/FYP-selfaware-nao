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

    def __init__(self, application, request, **kwargs):
        super(SocketHandler, self).__init__(application, request, **kwargs)
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

        print(type(robot_experience['target']))

        self.robotAwareness.interpret_robot_experience(robot_experience)

        # send_message = {}
        # send_message['data'] = 'I have received message'
        # self.command_robot_speak(send_message)

    def on_close(self):
        if self in cl:
            cl.remove(self)
            print('1 disconnected...')
        self.robotAwareness.exeProc.dialogueManager.reset()

    def command_robot_speak(self, message):
        """ encode dictionary message command to json and forward to robot """
        for conn in cl:
            conn.write_message(json.dumps(message))


app = web.Application([
    (r'/ws', SocketHandler),
])


if __name__ == '__main__':
    print("server listening on port 8888")
    app.listen(8888)
    ioloop.IOLoop.instance().start()
