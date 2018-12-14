from apis.text_semantics_analyzer import SemanticsAnalyzer
from threading import Thread
import time


class Interpreter(Thread):

    def __init__(self):
        super().__init__()
        self.sa = SemanticsAnalyzer()

    def perceive(self, robot_exp):
        """
        :sample robot experience:
        experience = {
            'subject': 'junjie',
            'target': 'me',
            'physicalAct': 'talking',
            'speech': 'hello there',
            'ambianceEmotion': {
                "agitationLevel" : 0.5,
                "calmLevel" : 0.5
            },
            'emotionalState': [0, 0, 0, 0, 0, 0, 0],
            'datetime': datetime.datetime(2018, 12, 14, 14, 7, 13, 815735),
            'place': [1.2931, 103.856]
        }
        """
        semantics = self.sa(robot_exp['speech'])
        # store robot experience to experiential aspect

    def start(self):
        self.running = True
        super().start()

    def run(self):
        self.idle()

    def stop(self):
        self.running = False

    def idle(self):
        while(self.running):
            time.sleep(0.2)


if __name__ == "__main__":
    interpreter = Interpreter()
    interpreter.daemon = True
    interpreter.start()

    while 1:
        time.sleep(1)
