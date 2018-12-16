from apis.text_semantics_analyzer import SemanticsAnalyzer
from apis.dialogue_act.DialogueActTagger import DialogueActTagger
from threading import Thread
import time


class Interpreter(Thread):

    def __init__(self, awareness):
        super().__init__()
        self.awareness = awareness
        self.sa = SemanticsAnalyzer()
        self.da = DialogueActTagger('apis\dialogue_act\model1')

    def perceive(self, robot_exp):
        """
        robot_exp = {
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
        dialog_acts = [{'dimension': 'SocialObligationManagement',
                        'communicative_function': 'Salutation'}]
        """
        # store robot experience to experiential aspect
        self.awareness.memory.save_experiential(robot_exp)

        semantics = self.sa(robot_exp['speech'])
        dialog_acts = self.da.dialogue_act_tag(robot_exp['speech'])

        # send perception to executive process
        self.awareness.exeProc.reason_perception(robot_exp, semantics, dialog_acts)

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
