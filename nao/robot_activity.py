import json
import time
from websocket import create_connection


def main():
    ws = create_connection("ws://127.0.0.1:8888/ws")

    while True:
        msgNum = raw_input('Enter message num')

        if msgNum == "0":
            ws.send(json.dumps({'type': 'reflect',
                                'data': {'identity': 'me',
                                         'act': 'talking',
                                         'speech': 'i am fine',
                                         'ambiance': [0, 1],
                                         'date': []
                                }
            }))
        if msgNum == "1":
            ws.send(json.dumps({'type': 'respond',
                                'data': {'identity': 'bob',
                                         'act': 'talking',
                                         'speech': 'how are you',
                                         'ambiance': [0, 1],
                                         'date': []
                                }
            }))
            response = ws.recv()
            print (json.loads(response))


if __name__ == "__main__":
    main()
