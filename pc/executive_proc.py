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


class DialogueManager():

    def __init__(self):
        self.state = START_STATE
        self.context = {}

    def advance_state(self, robot_exp, semantic, temporals, dialogue_acts):

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

            # if CONVERSATION_EXCEPTION:
            #     self.state = CONVERSATION_EXCEPT_STATE

            # if HUMAN_INDICATE_FEEDBACK_STATE:
            #     self.state = FEEDBACK_STATE

            # if HUMAN_INDICATE_CLOSING:
            #     self.state = CLOSING_STATE

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
                self.state = CONVERSATION_GENERAL_STATE

        elif self.state == FEEDBACK_STATE:
            for da in dialogue_acts:
                if da['dimension'] == 'SocialObligationManagement' \
                    and da['communicative_function'] == 'Salutation':
                    self.state = CLOSING_STATE

        elif self.state == CLOSING_STATE:
            if (robot_exp['target'] is None) \
                and (robot_exp['physicalAct'] == 'observing'):
                self.reset()

    def conv_is_aboutme(self, robot_exp, semantic, dialogue_acts):

        speech = robot_exp['speech']
        speaker = robot_exp['subject']
        listener = robot_exp['target']

        # TODO: RULES DETERMINING CONVERSATION ABOUT ME
        if speaker == 'me':
            if 'my' in semantic['subject']['text']:
                return True

            if 'i ' in semantic['subject']['text'] or \
               ' i ' in semantic['subject']['text']:
               return True

        if listener == 'me':
            if 'you' in semantic['subject']['text']:
                return True

            for da in dialogue_acts:
                if da['dimension'] == 'Task' \
                    and da['communicative_function'] == 'Directive':
                    return True

        return False

    def conv_is_abouthuman(self, robot_exp, semantic, dialogue_acts):

        speech = robot_exp['speech']
        speaker = robot_exp['subject']
        listener = robot_exp['target']

        # TODO: RULES DETERMINING CONVERSATION ABOUT HUMAN
        if speaker != 'me':
            if 'my' in semantic['subject']['text']:
                return True

            if 'i ' in semantic['subject']['text'] or \
               ' i ' in semantic['subject']['text']:
               return True

        if listener != 'me':
            if 'you' in semantic['subject']['text']:
                return True

            for da in dialogue_acts:
                if da['dimension'] == 'Task' \
                    and da['communicative_function'] == 'Directive':
                    return True

        return False

    def conv_have_time(self, temporals):
        if len(temporals) > 0:
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

    def reason_perception(self, robot_exp, semantic, temporals, dialogue_acts):
        speech = robot_exp['speech']
        speaker = robot_exp['subject']
        listener = robot_exp['target']

        # advance conversation state
        self.dialogueManager.advance_state(robot_exp, semantic, temporals, dialogue_acts)
        dialogue_state = self.dialogueManager.get_state()

        # no target to observe, robot does nothing with perception
        if (robot_exp['target'] is None) \
            and (robot_exp['physicalAct'] == 'observing'):
            return

        # does perception receive leads to memory storage ?

        # does perception receive requires robot response ?
        robot_respond = False
        if robot_exp['target'] = 'me':
            robot_respond = True

        if robot_respond:
            # a --- mapping concept analysis to robot response
            #           dialogue_state + semantic + dialogue_acts
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
