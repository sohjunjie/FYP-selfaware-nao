import logging
from websocket import create_connection


PC_ADDR = '192.168.0.102'
PC_PORT = '8888'
ROBOT_IP = '127.0.0.1'
ROBOT_PORT = 9559


def init():

    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%d-%m-%Y:%H:%M:%S',
                        level=logging.INFO)

    global WS
    WS = None
    try:
        WS = create_connection("ws://" + PC_ADDR +  ":" + PC_PORT + "/ws")
        logging.info('connected to remote laptop')
    except:
        logging.info('fail to connect to remote laptop')
