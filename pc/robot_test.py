from datetime import datetime as dt
from apis.text_tone_analyzer import ToneAnalyzer
from apis.geocoder_ip import get_robot_location
from awareness import RobotAwareness
import json
import os
import time


human_tracked = 'john'
ta = ToneAnalyzer()


class RobotMocker():

    def __init__(self):
        self.awareness = None

    def command_robot_speak(self, message):

        robot_speech = message['data']
        if robot_speech == '':
            print("R: your turn to speak")

        else:
            print("R: " + robot_speech)

            # robot spoke
            experience = {
                'subject': 'me',
                'target': human_tracked,
                'physicalAct': 'talking',
                'speech': robot_speech,
                'ambianceEmotion': { "agitationLevel" : 0, "calmLevel" : 0 }
            }
            experience['emotionalState'] = list(ta.get_tone_from_text(experience['speech']).values())
            experience['datetime'] = dt.now()
            experience['place'] = get_robot_location()

            self.awareness.interpret_robot_experience(experience)


def main():

    rm = RobotMocker()

    robotAwareness = RobotAwareness(rm)
    rm.awareness = robotAwareness

    while 1:
        experience = None
        cmd = input('Enter command: ')
        robot_exp = parse_command(cmd)

        robotAwareness.interpret_robot_experience(robot_exp)

        if cmd == '[C]':
            break


def parse_command(cmd):

    if cmd == '[E]':
        # human found
        experience = {
            'subject': 'me',
            'target': human_tracked,
            'physicalAct': 'observing',
            'speech': '',
            'ambianceEmotion': { "agitationLevel" : 0, "calmLevel" : 0 }
        }
    elif cmd == '[C]':
        # human lost
        experience = {
            'subject': 'me',
            'target': None,
            'physicalAct': 'observing',
            'speech': '',
            'ambianceEmotion': { "agitationLevel" : 0, "calmLevel" : 0 }
        }
    else:
        # human spoke
        experience = {
            'subject': human_tracked,
            'target': 'me',
            'physicalAct': 'talking',
            'speech': cmd,
            'ambianceEmotion': { "agitationLevel" : 0, "calmLevel" : 0 }
        }
    experience['emotionalState'] = list(ta.get_tone_from_text(experience['speech']).values())
    experience['datetime'] = dt.now()
    experience['place'] = get_robot_location()

    return experience


if __name__ == '__main__':
    main()
