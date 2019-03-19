import logging


class Reaction():

    def __init__(self, awareness, wsApp):
        super().__init__()
        self.awareness = awareness
        self.wsApp = wsApp

    def speak(self, speech):

        logging.info("Awareness Reaction: Received robot response")

        send_message = {}
        send_message['data'] = speech

        logging.info("Awareness Reaction: Command Nao Action: Speak")
        self.wsApp.command_robot_speak(send_message)
