from apis.text_semantics_analyzer import SemanticsAnalyzer
from apis.dialogue_act.DialogueActTagger import DialogueActTagger
from config import SUTIME_JARS
from sutime import SUTime


class Interpreter():

    def __init__(self, awareness):
        super().__init__()
        self.awareness = awareness
        self.sa = SemanticsAnalyzer()
        self.da = DialogueActTagger('apis\dialogue_act\model1')
        self.sutime = SUTime(jars=SUTIME_JARS, mark_time_ranges=True)

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
        semantics = [{'subject': {'text': 'my favourite color'},
                      'sentence': 'my favourite color is blue',
                      'object': {'text': 'blue'},
                      'action': {'verb': {'text': 'be',
                                          'tense': 'present'},
                                 'text': 'is',
                                 'normalized': 'be'}
                     }]
        """
        # store robot experience to experiential aspect
        self.awareness.memory.save_experiential(robot_exp)

        # semantic analysis
        semantic = None
        semantics = self.sa(robot_exp['speech'])
        if len(semantics) > 0:
            semantic = semantics[-1]
        else:
            semantic = {'subject': {'text': ''},
                        'sentence': robot_exp['speech'],
                        'object': {'text': ''},
                        'action': {}
            }

        # temporal analysis
        temporals = self.sutime.parse(robot_exp['speech'])

        dialog_acts = self.da.dialogue_act_tag(robot_exp['speech'])

        # send perception to executive process
        self.awareness.exeProc.reason_perception(robot_exp, semantic, temporals, dialog_acts)
