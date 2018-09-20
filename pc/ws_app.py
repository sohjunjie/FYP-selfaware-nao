from gensim.models import Word2Vec
from tornado import websocket, web, ioloop
import json
import os

cl = []
MODELS_DIR = 'models/'
model_gs = Word2Vec.load(os.path.join(MODELS_DIR, 'text8_gs.bin'))


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
        send_message['data'] = message
        for conn in cl:
            conn.write_message(send_message)

    def on_close(self):
        if self in cl:
            cl.remove(self)
            print('1 disconnected...')

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
