import time, threading, websocket


PC_ADDR = '192.168.0.102'
PC_PORT = '8888'
ROBOT_IP = '127.0.0.1'
ROBOT_PORT = 9559


def init_robot_websocket(callback):
    rws_thread = RobotWebSocket(callback)
    rws_thread.daemon = True
    rws_thread.start()
    time.sleep(2)       # let the websocket establish connection
    return rws_thread


class RobotWebSocket(threading.Thread):
    def __init__(self, onMessageCallback):
        super(RobotWebSocket, self).__init__()

        def on_message(ws, message):
            onMessageCallback(message)

        def on_error(ws, error):
            print error

        def on_close(ws):
            print "### closed ###"

        # self.ws = websocket.WebSocketApp("ws://echo.websocket.org/",
        self.ws = websocket.WebSocketApp("ws://" + PC_ADDR +  ":" + PC_PORT + "/ws",
                                            on_message = on_message,
                                            on_error = on_error,
                                            on_close = on_close)

    def run(self):

        def on_open(ws):
            print "### opened ###"

        self.ws.on_open = on_open
        self.ws.run_forever()


if __name__ == "__main__":

    def callback(msg):
        print 'callback: ' + msg

    rws_thread = RobotWebSocket(callback)
    rws_thread.daemon = True
    rws_thread.start()

    while 1:
        msg = raw_input('message_to_send: ')
        rws_thread.ws.send(msg)
