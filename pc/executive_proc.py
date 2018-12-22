from threading import Thread
import time


START_STATE = 0
GREETING_STATE = 1
FEEDFORWARD_STATE = 2
CONVERSATION_EXCEPT_STATE = 3
CONVERSATION_ABOUTME_STATE = 4
CONVERSATION_MYACTIVITY_STATE = 5
CONVERSATION_GENERAL_STATE = 6
CONVERSATION_ABOUTHUMAN_STATE = 7
CONVERSATION_HUMANACTIVITY_STATE = 8
FEEDBACK_STATE = 9
CLOSING_STATE = 10
END_STATE = 11

TIME_KEYWORDS = [
    'the day before yesterday',
    'the day after tomorrow',
    'the day before',
    'last century',
    'next month',
    'last month',
    'yesterday',
    'next week',
    'last year',
    'last week',
    'millenium',
    'next year',
    'just now',
    'recently',
    'tomorrow',
    'century',
    'weekend',
    'before',
    'decade',
    'today',
    'month',
    'after',
    'week',
    'year',
    'now',
    'ago',
    'day']


class DialogueManager():

    def __init__(self):
        self.state = START_STATE
        self.context = {}

    def advance_state(self, robot_exp, semantics, dialogue_acts):

        if self.state == START_STATE:
            # advance to greeting state if dialogue act is salutation
            for da in dialogue_acts:
                if da['dimension'] == 'SocialObligationManagement' \
                    and da['communicative_function'] == 'Salutation':
                    self.state = GREETING_STATE

        elif self.state == GREETING_STATE:
            # advance to feedforward state if dialogue act is anything
            # other than salutation
            for da in dialogue_acts:
                if da['dimension'] == 'SocialObligationManagement' \
                    and da['communicative_function'] == 'Salutation':
                    return
            self.state = FEEDFORWARD_STATE

        elif (self.state == FEEDFORWARD_STATE) or \
            (self.state > FEEDFORWARD_STATE and self.state < FEEDBACK_STATE):

            if self.conv_is_aboutme(robot_exp, semantics, dialogue_acts):
                if self.conv_have_time(robot_exp, semantics, dialogue_acts):
                    self.state = CONVERSATION_MYACTIVITY_STATE
                else:
                    self.state = CONVERSATION_ABOUTME_STATE

            if self.conv_is_abouthuman(robot_exp, semantics, dialogue_acts):
                if self.conv_have_time(robot_exp, semantics, dialogue_acts):
                    self.state = CONVERSATION_HUMANACTIVITY_STATE
                else:
                    self.state = CONVERSATION_ABOUTHUMAN_STATE

        elif self.state > FEEDFORWARD_STATE and self.state < FEEDBACK_STATE:
            pass

        elif self.state == FEEDBACK_STATE:
            pass

        elif self.state == CLOSING_STATE:
            pass

    def conv_is_aboutme(self, robot_exp, semantics, dialogue_acts):

        speech = robot_exp['speech']
        speaker = robot_exp['subject']
        listener = robot_exp['target']

        # TODO: RULES DETERMINING CONVERSATION ABOUT ME
        if speaker == 'me':
            if 'my' in semantics[0]['subject']['text']:
                return True

            if 'i ' in semantics[0]['subject']['text'] or \
               ' i ' in semantics[0]['subject']['text']:
               return True

        if listener == 'me':
            if 'you' in semantics[0]['subject']['text']:
                return True

            for da in dialogue_acts:
                if da['dimension'] == 'Task' \
                    and da['communicative_function'] == 'Directive':
                    return True

    def conv_is_abouthuman(self, robot_exp, semantics, dialogue_acts):
        # TODO: RULES DETERMINING CONVERSATION ABOUT HUMAN
        if speaker != 'me':
            if 'my' in semantics[0]['subject']['text']:
                return True

            if 'i ' in semantics[0]['subject']['text'] or \
               ' i ' in semantics[0]['subject']['text']:
               return True

        if listener != 'me':
            if 'you' in semantics[0]['subject']['text']:
                return True

            for da in dialogue_acts:
                if da['dimension'] == 'Task' \
                    and da['communicative_function'] == 'Directive':
                    return True

    def conv_have_time(self, robot_exp, semantics, dialogue_acts):
        # TODO: RULES DETERMINING CONVERSATION HAS TIME ELEMENT
        if 'yesterday' in semantics[0]['sentence']:
            return True

        return False

    def reset(self):
        self.state = START_STATE
        self.context = {}

    def get_state(self):
        return self.state


class ExecutiveProc(Thread):

    def __init__(self, awareness):
        super().__init__()
        self.awareness = awareness
        self.dialogueManager = DialogueManager()

    def reason_perception(self, robot_exp, semantics, dialogue_acts):
        speech = robot_exp['speech']
        speaker = robot_exp['subject']
        listener = robot_exp['target']

        # advance conversation state
        self.dialogueManager.advance_state(robot_exp, semantics, dialogue_acts)
        dialogue_state = self.dialogueManager.get_state()

        # does perception receive leads to memory storage ?

        # does perception receive requires robot response ?
        robot_respond = False
        if robot_exp['target'] = 'me':
            robot_respond = True

        if robot_respond:
            # a --- mapping concept analysis to robot response
            #           dialogue_state + semantics + dialogue_acts
            # b --- pull required information from memory
            pass    # speech = sth
        else:
            pass    # speech = empty

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
