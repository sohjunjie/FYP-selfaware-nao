from tornado import websocket, web, ioloop
from datetime import datetime as dt
import json
import os
import time


cl = []


class SocketHandler(websocket.WebSocketHandler):

    def check_origin(self, origin):
        return True

    def open(self):
        if self not in cl:
            cl.append(self)
            print(str(len(cl)) + ' connected...')

    def on_message(self, message):
        print("receive " + message)

        send_message = {}
        send_message['data'] = 'I have received message'
        self.command_robot_speak(send_message)

    def on_close(self):
        if self in cl:
            cl.remove(self)
            print('1 disconnected...')

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
