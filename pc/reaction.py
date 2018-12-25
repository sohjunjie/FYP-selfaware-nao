
class Reaction():

    def __init__(self, awareness, wsApp):
        super().__init__()
        self.awareness = awareness
        self.wsApp = wsApp

    def speak(self, speech):
        send_message = {}
        send_message['data'] = speech
        self.wsApp.command_robot_speak(send_message)
