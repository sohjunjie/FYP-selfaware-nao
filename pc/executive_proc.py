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
CONVERSATION_FEEDBACK_STATE = 9
CONVERSATION_CLOSING_STATE = 10


class DialogueManager():

    def __init__(self):
        self.state = START_STATE

    def advance_state(self, speech):
        pass


class ExecutiveProc(Thread):

    def __init__(self):
        super().__init__()

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
    exeProc = ExecutiveProc()
    exeProc.daemon = True
    exeProc.start()

    while 1:
        time.sleep(1)
