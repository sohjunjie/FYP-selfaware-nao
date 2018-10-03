import logging
from websocket import create_connection


PC_ADDR = '192.168.0.102'
PC_PORT = '8888'

ROBOT_IP = '127.0.0.1'
ROBOT_PORT = 9559

PROMPT_PATH = '/home/nao/recordings/microphones/siri1.wav'
PROMPT_ENDP = '/home/nao/recordings/microphones/siri2.wav'
RECORD_PATH = '/home/nao/recordings/microphones/temp.wav'


def init():

    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%d-%m-%Y:%H:%M:%S',
                        level=logging.INFO)

    global WS
    try:
        WS = create_connection("ws://" + PC_ADDR +  ":" + PC_PORT + "/ws")
    except:
        WS = None
