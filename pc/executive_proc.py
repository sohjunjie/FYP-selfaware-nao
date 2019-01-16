import re
from datetime import datetime
from concept_analysis import ConceptAnalyzer
import concepts

from apis import utils
from config import START_STATE
from config import GREETING_STATE
from config import FEEDFORWARD_STATE
from config import CONVERSATION_STATE
from config import CONVERSATION_EXCEPT_STATE
from config import CONVERSATION_ABOUTME_STATE
from config import CONVERSATION_MYACTIVITY_STATE
from config import CONVERSATION_GENERAL_STATE
from config import CONVERSATION_ABOUTHUMAN_STATE
from config import CONVERSATION_HUMANACTIVITY_STATE
from config import FEEDBACK_STATE
from config import CLOSING_STATE
from config import END_STATE


class DialogueManager():

    def __init__(self, memory):
        self.memory = memory
        self.reset()

    def advance_state(self, robot_exp, semantic, temporals, dialogue_acts):

        # reset dialogue manager if human exited
        if (robot_exp['target'] is None) and (robot_exp['physicalAct'] == 'observing'):
            self.reset()

        if (not robot_exp['target'] is None) and (robot_exp['physicalAct'] == 'observing'):
            self.context['conv_started_datetime'] = datetime.now()    # conversation started

        if self.state == START_STATE:
            # advance to greeting state if dialogue act is salutation
            if any((x['dimension'] == 'SocialObligationManagement' \
                and x['communicative_function'] == 'Salutation') for x in dialogue_acts):
                self.state = GREETING_STATE
                if robot_exp['subject'] == 'me':
                    self.context['robot_greeted'] = True


        elif self.state == GREETING_STATE:
            # advance to feedforward state if dialogue act is no longer salutation
            if not any((x['dimension'] == 'SocialObligationManagement' \
                    and x['communicative_function'] == 'Salutation') for x in dialogue_acts):
                self.state = FEEDFORWARD_STATE
            else:
                # it is a saluation by the robot, robot_greeted flag raised
                if robot_exp['subject'] == 'me':
                    self.context['robot_greeted'] = True

        elif (self.state >= FEEDFORWARD_STATE) and (self.state < FEEDBACK_STATE):

            # response of robot to a feedforward message cause state to still be feedforward
            if 'prev_speech' in self.context and \
                self.context['prev_speech']['isfeedforward'] and \
                (
                    any(x['communicative_function'] == 'PropQ' 
                        for x in self.context['prev_speech']['dialogue_acts'])
                        or
                    any(x['communicative_function'] == 'SetQ'
                        for x in self.context['prev_speech']['dialogue_acts'])
                ) and \
                any(x['communicative_function'] == 'Statement' for x in dialogue_acts):
                    return

            if self.is_phatic_message(robot_exp, dialogue_acts, semantic):
                return

            # if CONVERSATION_EXCEPTION:
            #     self.state = CONVERSATION_EXCEPT_STATE

            if self.is_feedback_state(robot_exp):
                self.state = FEEDBACK_STATE
                return

            if self.is_closing_state(robot_exp):
                self.state = CLOSING_STATE
                return

            if self.conv_is_aboutme(robot_exp, semantic, dialogue_acts):
                if self.conv_have_time(temporals):
                    self.state = CONVERSATION_MYACTIVITY_STATE
                else:
                    self.state = CONVERSATION_ABOUTME_STATE

            elif self.conv_is_abouthuman(robot_exp, semantic, dialogue_acts):
                if self.conv_have_time(temporals):
                    self.state = CONVERSATION_HUMANACTIVITY_STATE
                else:
                    self.state = CONVERSATION_ABOUTHUMAN_STATE

            else:
                # return
                self.state = CONVERSATION_GENERAL_STATE

        elif self.state == FEEDBACK_STATE:
            if self.is_closing_state(robot_exp):
                # if any((x['dimension'] == 'SocialObligationManagement' \
                #     and x['communicative_function'] == 'Salutation') for x in dialogue_acts):
                self.state = CLOSING_STATE

        elif self.state == CLOSING_STATE:
            if (robot_exp['target'] is None) \
                and (robot_exp['physicalAct'] == 'observing'):
                self.reset()

    def is_phatic_message(self, robot_exp, dialogue_acts, semantic):

        if any((x['dimension'] == 'Task' and
                x['communicative_function'] == 'Statement') for x in dialogue_acts):

            if semantic['subject']['text'] == 'we' and semantic['action']['normalized'] == 'have':
                return True
            if semantic['subject']['text'] == 'that' and semantic['action']['normalized'] == 'be':
                return True

        if robot_exp['speech'] in concepts.COMMON_RESPONSE_MAPPINGS:
            return True

        return False

    def conv_is_aboutme(self, robot_exp, semantic, dialogue_acts):

        speaker = robot_exp['subject']
        listener = robot_exp['target']

        # if dialogue act is a question, check semantic object for my, i, me, you,
        if any((x['dimension'] == 'Task' \
            and x['communicative_function'] == 'Directive') for x in dialogue_acts):
            if listener == 'me'and any(x in semantic['object']['text'] 
                                            for x in ['my', 'i ', ' i ', 'me']):
                return False
            return True

        # TODO: RULES DETERMINING CONVERSATION ABOUT ME
        if speaker == 'me':
            if 'my' in semantic['subject']['text']:
                return True

            if 'i ' in semantic['subject']['text'] or \
               ' i ' in semantic['subject']['text'] or \
               semantic['subject']['text'] == 'i':
               return True

            if 'me' in semantic['subject']['text']:
                return True

        if listener == 'me':
            if 'you' in semantic['subject']['text']:
                return True

        if self.state == CONVERSATION_ABOUTME_STATE and \
            'we' in semantic['subject']['text']:
            return True

        return False

    def conv_is_abouthuman(self, robot_exp, semantic, dialogue_acts):

        speaker = robot_exp['subject']
        listener = robot_exp['target']

        # if dialogue act is a question, check semantic object for my, i, me, you,
        if any((x['dimension'] == 'Task' \
            and x['communicative_function'] == 'Directive') for x in dialogue_acts):
            if listener == 'me'and any(x in semantic['object']['text']
                                            for x in ['my', 'i ', ' i ', 'me']):
                return True
            return False

        # TODO: RULES DETERMINING CONVERSATION ABOUT HUMAN
        if speaker != 'me':
            if 'my' in semantic['subject']['text']:
                return True

            if semantic['subject']['text'] == 'me':
                return True

            if 'i ' in semantic['subject']['text'] or \
               ' i ' in semantic['subject']['text'] or \
               semantic['subject']['text'] == 'i':
               return True

        if listener != 'me':
            if 'you' in semantic['subject']['text']:
                return True

        if self.state == CONVERSATION_ABOUTHUMAN_STATE and \
            'we' in semantic['subject']['text']:
            return True

        return False

    def is_feedback_state(self, robot_exp):
        if robot_exp['speech'] in concepts.COMMON_FEEDBACK:
            return True
        return False

    def is_closing_state(self, robot_exp):
        print(robot_exp['speech'])
        closing_keywords = [
            'have to go',
            'got to go',
            'need to leave'
        ]
        if any(x in robot_exp['speech'] for x in closing_keywords):
            return True
        return False

    def conv_have_time(self, temporals):
        if len(temporals) > 0:
            return True
        return False

    def reset(self):
        self.state = START_STATE
        self.context = {}

        h = datetime.now().hour

        self.context['partsOfDay'] = "morning" if (h >= 0 and h < 12) else \
                                    ("afternoon" if (h >= 12 and h < 17) else \
                                    "evening")

        self.context['name'] = self.memory.get_robot_name()
        self.context['robot_greeted'] = False
        self.context['robot_bid_farewell'] = False
        self.context['conv_started_datetime'] = None
        self.context['conversation_id'] = None

    def get_state(self):
        return self.state


class ExecutiveProc():

    def __init__(self, awareness):
        super().__init__()
        self.awareness = awareness
        self.dialogueManager = DialogueManager(self.awareness.memory)
        self.conceptAnalyzer = ConceptAnalyzer(self.awareness.memory, self.dialogueManager)

    def reason_perception(self, robot_exp, semantics, temporals, dialogue_acts):
        speech = robot_exp['speech']
        speaker = robot_exp['subject']
        listener = robot_exp['target']

        # advance conversation state
        self.dialogueManager.advance_state(robot_exp,
                                           max(semantics, key=lambda x: utils.extract_relevant_semantic(x)),
                                           temporals,
                                           dialogue_acts)
        dialogue_state = self.dialogueManager.get_state()

        print('state: ', dialogue_state)

        # no target to observe, robot does nothing with perception
        if (robot_exp['target'] is None) \
            and (robot_exp['physicalAct'] == 'observing'):
            return

        # 1 - does perception receive leads to memory storage ?
        self.learn_from_experience(robot_exp, semantics, dialogue_acts, temporals)


        # 2 - does perception receive requires robot response ?
        robot_respond = False
        if robot_exp['target'] == 'me':
            robot_respond = True
            self.dialogueManager.context['human'] = robot_exp['subject']

        if robot_exp['subject'] == 'me' \
            and not robot_exp['target'] is None \
            and robot_exp['physicalAct'] == 'observing':
            robot_respond = True        # robot start prompt if human remain unspoken for 10s
            self.dialogueManager.context['human'] = robot_exp['target']

        print(dialogue_state)

        if robot_respond:
            # a --- mapping concept analysis to robot response
            #           dialogue_state + semantic + dialogue_acts
            response = self.conceptAnalyzer.concept_to_response(dialogue_state,
                                                                semantics,
                                                                dialogue_acts,
                                                                self.dialogueManager.context,
                                                                temporals,
                                                                robot_exp)

            # b --- pull required information from memory
            response = self.resolve_response(response, self.dialogueManager.context)
            self.awareness.reaction.speak(response)
        else:
            self.awareness.reaction.speak('')

    def resolve_response(self, response, context):

        params = re.findall(r"\{([A-Za-z0-9_ ]+)\}", response)
        params_values = []
        if self.dialogueManager.get_state() == CONVERSATION_ABOUTME_STATE:
            params_values = [(key, context[key])
                                if key in context
                                else (key, self.awareness.memory.query_robot(key))
                             for key in params]

        elif self.dialogueManager.get_state() == CONVERSATION_ABOUTHUMAN_STATE:
            params_values = [(key, context[key])
                                if key in context
                                else (key, self.awareness.memory.query_human(context['human'], key))
                             for key in params]
        else:
            params_values = [(key, context[key])
                                if key in context 
                                else (key, '')
                             for key in params]

        response_params = dict(params_values)

        return response.format(**response_params)

    def learn_from_experience(self, robot_exp, semantics, dialogue_acts, temporals):
        """
        empty_semantics = [{
            'subject': {'text': ''},
            'sentence': robot_exp['speech'],
            'object': {'text': ''},
            'action': {}
        }]

        semantics = [{
            "subject": { "text": "my favourite color" },
            "sentence": "my favourite color is blue",
            "object": { "text": "blue" },
            "action": {
                "verb": {
                    "text": "be",
                    "tense": "present"
                },
                "text": "is",
                "normalized": "be"
            }
        }]
        """

        if any(len(x['action'].keys()) == 0 for x in semantics):
            return      # nothing to learn from robot experience

        if robot_exp['subject'] == 'me':
            return      # robot learns nothing new from its own speech

        if not any(x['communicative_function'] == 'Statement' for x in dialogue_acts):
            return      # robot learns nothing when dialogue is not a statement

        for semantic in semantics:
            if semantic['action']['normalized'] == 'be':

                conv_state = self.dialogueManager.get_state()
                prop_name = utils.strip_possessive(semantic['subject']['text'])
                prop_name = 'occupation' if prop_name == 'i' else prop_name
                prop_value = semantic['object']['text']

                # something new was learnt about human
                if conv_state == CONVERSATION_ABOUTHUMAN_STATE:
                    person = robot_exp['subject']
                    props = {
                        'property_name': prop_name,
                        'property_type': 'str',
                        'property_value_str': prop_value
                    }
                    success = self.awareness.memory.update_social_prop(person, props)
                    if not success:
                        print("warning: prop_name={prop_name} of {person} with value={prop_value} not saved"
                            .format(prop_name=prop_name,
                                    person=person,
                                    prop_value=prop_value))
