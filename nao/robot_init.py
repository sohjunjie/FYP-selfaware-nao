import logging
import json
import sys
import time
import threading
from naoqi import ALProxy, ALBroker, ALModule
import config as cf


global stimuliEventWatcher


class WorldStimuliEventWatcher(ALModule):
    """ A module to react to world stimuli """

    def __init__(self):
        ALModule.__init__(self, "stimuliEventWatcher")

        # self.asr = ALProxy("ALSpeechRecognition", cf.ROBOT_IP, cf.ROBOT_PORT)
        # self.asr.setLanguage("English")
        # self.asr.pause(True)
        # with open('dictionary.txt') as f:
        #     self.asr.setVocabulary(['hello', 'robot', 'cool'], False)
        # self.asr.pause(False)
        # self.al_mood = ALProxy("ALMood", cf.ROBOT_IP, cf.ROBOT_PORT)
        self.dialog = ALProxy('ALDialog', cf.ROBOT_IP, cf.ROBOT_PORT)
        self.dialog.setLanguage("English")
        self.dialog_topic = self.dialog.loadTopic('/var/persistent/home/nao/HumanDialog/HumanDialog_enu.top')
        self.dialog.subscribe('myModule')
        self.dialog.activateTopic(self.dialog_topic)
        self.basic_awareness = ALProxy("ALBasicAwareness", cf.ROBOT_IP, cf.ROBOT_PORT)
        # self.basic_awareness.setEngagementMode("FullyEngaged")
        self.basic_awareness.startAwareness()
        self.motion = ALProxy("ALMotion", cf.ROBOT_IP, cf.ROBOT_PORT)
        self.motion.wakeUp()

        self.memory = ALProxy("ALMemory", cf.ROBOT_IP, cf.ROBOT_PORT)
        self.memory.subscribeToEvent("ALBasicAwareness/HumanTracked",
                                     "stimuliEventWatcher",
                                     "onHumanTracked")
        self.memory.subscribeToEvent("ALBasicAwareness/HumanLost",
                                     "stimuliEventWatcher",
                                     "onHumanLost")
        self.memory.subscribeToEvent("FaceDetected",
                                     "stimuliEventWatcher",
                                     "onFaceDetected")

        self.tts = ALProxy("ALTextToSpeech", cf.ROBOT_IP, cf.ROBOT_PORT)
        self.is_sound_detection_started = True
        self.is_face_detection_started = True
        self.is_human_tracked = False
        self.is_dialog_detection_started = False
        self.got_face = False
        self.human_spoke = False
        self.human_tracked = None
        self.rws_thread = cf.init_robot_websocket(self.handleRemotePCAwarenessResponse)

        print ""
        print ""
        print ""
        print ""
        print "==========Initialized=========="

    def say(self, msg):
        self.stop_dialog_detection()
        self.tts.say(msg)
        self.start_dialog_detection()

    def onHumanTracked(self, key, value, msg):
        """ callback for event HumanTracked """
        self.is_human_tracked = True
        # self.stop_sound_detection()
        self.start_dialog_detection()
        if value >= 0:
            logging.info("Got HumanTracked: detected person with ID:" + str(value))

    def onHumanLost(self, key, value, msg):
        """ callback for event HumanLost """
        self.is_human_tracked = False
        self.human_tracked = None
        logging.info("Got HumanLost: lost human with ID:" + str(value))
        self.stop_dialog_detection()
        # self.start_sound_detection()

        # scenario5: human leaves conversation
        experience = {
            'subject': 'me',
            'target': None,
            'physicalAct': 'observing',
            'speech': '',
            # 'ambianceEmotion': self.al_mood.ambianceState()
            'ambianceEmotion': {
                "agitationLevel" : 0,
                "calmLevel" : 0
            }
        }
        # AmbianceData = {
        #     "agitationLevel" : value,
        #     "calmLevel" : value
        # }
        # [emotionalState, datetime, place] details capture in remote laptop
        self.start_face_detection()

        logging.info("Got HumanLost: Informing Awareness that human exited")
        self.rws_thread.ws.send(json.dumps(experience))

    def onFaceDetected(self, key, value, msg):
        if value == []:
            # empty value when the face disappears
            self.got_face = False
            self.human_tracked = None
        elif not self.got_face:
            # only speak the first time a face appears
            self.stop_face_detection()
            self.got_face = True
            self.human_tracked = value[1][0][1][2] if value[1][0][1][2] != '' else 'stranger'
            self.say("I see you, " + self.human_tracked + ".")

            logging.info("Face detected: Detected human: " + self.human_tracked)

            # scenario1: robot see human
            experience = {
                'subject': 'me',
                'target': self.human_tracked,
                'physicalAct': 'observing',
                'speech': '',
                # 'ambianceEmotion': self.al_mood.ambianceState()
                'ambianceEmotion': {
                    "agitationLevel" : 0,
                    "calmLevel" : 0
                }
            }
            # [emotionalState, datetime, place] details capture in remote laptop
            logging.info("Face detected: Informing Awareness that <human:" + self.human_tracked + "> was found")
            self.rws_thread.ws.send(json.dumps(experience))

    def onDialogDetected(self, key, value, msg):
        print value
        if not value:
            logging.info("Dialog detected: Unable to detect correctly")
            return
        if self.got_face and self.human_tracked:
            logging.info("Dialog detected: " + value)
            self.human_spoke = True
            # scenario3: human respond to robot
            experience = {
                'subject': self.human_tracked,
                'target': 'me',
                'physicalAct': 'talking',
                'speech': value,
                # 'ambianceEmotion': self.al_mood.ambianceState()
                'ambianceEmotion': {
                    "agitationLevel" : 0,
                    "calmLevel" : 0
                }
            }
            # [emotionalState, datetime, place] details capture in remote laptop
            logging.info("Dialog detected: Sending detected dialog to Awareness")
            self.rws_thread.ws.send(json.dumps(experience))

    def handleRemotePCAwarenessResponse(self, resp):
        """
        Websocket callback handler that manages remote PC
        speech response on the following dimensions.
        1. TTS conversion of robot response
        2. Synthesise robot response into robot experience, thus
           generating a feedback loop to the remote PC
        """
        response = json.loads(resp)
        robot_speech = str(response['data'])

        if len(robot_speech) == 0:
            logging.info("Websocket Handler: Awareness awaiting human dialog")
            # self.say('please go ahead.')
            # set time out 10s and give observing cue
            # self.human_spoke = False
            # threading.Timer(10, self.observeHuman).start()
            return

        logging.info("Websocket Handler: Awareness generated response: " + robot_speech)
        experience = {
            'subject': 'me',
            'target': self.human_tracked,
            'physicalAct': 'talking',
            'speech': robot_speech,
            # 'ambianceEmotion': self.al_mood.ambianceState()
            'ambianceEmotion': {
                "agitationLevel" : 0,
                "calmLevel" : 0
            }
        }
        # [emotionalState, datetime, place] details capture in remote laptop
        self.say(robot_speech)

        logging.info("Websocket Handler: Feeding generated response to Awareness")
        self.rws_thread.ws.send(json.dumps(experience))

    def observeHuman(self):
        # human have spoken within t seconds threshold
        if self.human_spoke:
            return

        # human have not spoken within t seconds threshold, send observation cue
        # that prompts robot to lead the conversation
        experience = {
            'subject': 'me',
            'target': self.human_tracked,
            'physicalAct': 'observing',
            'speech': '',
            # 'ambianceEmotion': self.al_mood.ambianceState()
            'ambianceEmotion': {
                "agitationLevel" : 0,
                "calmLevel" : 0
            }
        }
        self.rws_thread.ws.send(json.dumps(experience))

    def start_face_detection(self):
        if not self.is_face_detection_started:
            try:
                self.memory.subscribeToEvent("FaceDetected",
                                            "stimuliEventWatcher",
                                            "onFaceDetected")
            except RuntimeError:
                print "Face detection already started"
            self.is_face_detection_started = True

    def stop_face_detection(self):
        if self.is_face_detection_started:
            self.memory.unsubscribeToEvent("FaceDetected", "stimuliEventWatcher")
            self.is_face_detection_started = False

    def start_sound_detection(self):
        if not self.is_sound_detection_started:
            try:
                self.memory.subscribeToEvent("ALSoundLocalization/SoundLocated",
                                        "stimuliEventWatcher",
                                        "onSoundLocated")
            except RuntimeError:
                print "ASL already started"
            self.is_sound_detection_started = True

    def stop_sound_detection(self):
        if self.is_sound_detection_started:
            self.memory.unsubscribeToEvent("ALSoundLocalization/SoundLocated", "stimuliEventWatcher")
            self.is_sound_detection_started = False

    def start_dialog_detection(self):
        if not self.is_dialog_detection_started:
            try:
                self.memory.subscribeToEvent("Dialog/LastInput",
                                            "stimuliEventWatcher",
                                            "onDialogDetected")
            except RuntimeError:
                print "DL already started"
            self.is_dialog_detection_started = True

    def stop_dialog_detection(self):
        if self.is_dialog_detection_started:
            self.memory.unsubscribeToEvent("Dialog/LastInput", "stimuliEventWatcher")
            self.is_dialog_detection_started = False

    def on_stop(self):
        self.dialog.unsubscribe('myModule')
        self.dialog.deactivateTopic(self.dialog_topic)
        self.dialog.unloadTopic(self.dialog_topic)
        self.basic_awareness.stopAwareness()
        self.motion.rest()


if __name__ == "__main__":

    logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%d-%m-%Y:%H:%M:%S',
                        level=logging.INFO)

    event_broker = ALBroker("event_broker", "0.0.0.0", 0, cf.ROBOT_IP, cf.ROBOT_PORT)
    stimuliEventWatcher = WorldStimuliEventWatcher()

    #loop on, wait for events until interruption
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print "Interrupted by user, shutting down"
        stimuliEventWatcher.on_stop()
        event_broker.shutdown()
        sys.exit(0)
