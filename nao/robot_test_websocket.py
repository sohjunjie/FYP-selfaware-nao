import logging
import json
import sys
import time
import threading
import time
import config as cf


def handleRemotePCAwarenessResponse(resp):
    response = json.loads(resp)
    robot_speech = response['data']
    print robot_speech


if __name__ == "__main__":

    rws_thread = cf.init_robot_websocket(handleRemotePCAwarenessResponse)
    experience = {
        'subject': 'john',
        'target': 'me',
        'physicalAct': 'observing',
        'speech': '',
        'ambianceEmotion': {
            "agitationLevel" : 0,
            "calmLevel" : 0
        }
    }
    jexp = json.dumps(experience)
    print 'sending...'
    rws_thread.ws.send(jexp)
    print 'waiting...'

    while 1:
        time.sleep(0.5)
