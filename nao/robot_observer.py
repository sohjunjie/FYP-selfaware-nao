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
        self.is_human_tracked = False
        self.got_face = False
        self.human_spoke = False
        self.human_tracked = None

    def say(self, msg):
        self.tts.say(msg)

    def onHumanTracked(self, key, value, msg):
        """ callback for event HumanTracked """
        self.is_human_tracked = True
        if value >= 0:
            logging.info("got HumanTracked: detected person with ID:" + str(value))

    def onHumanLost(self, key, value, msg):
        """ callback for event HumanLost """
        self.is_human_tracked = False
        self.human_tracked = None
        print "human lost"

        try:
            self.memory.subscribeToEvent("FaceDetected",
                                        "stimuliEventWatcher",
                                        "onFaceDetected")
        except RuntimeError:
            print "Face detection already started"



    def onFaceDetected(self, key, value, msg):
        if value == []:
            # empty value when the face disappears
            self.got_face = False
            self.human_tracked = None
            print "face gone"
        elif not self.got_face:
            self.memory.unsubscribeToEvent("FaceDetected", "stimuliEventWatcher")
            # only speak the first time a face appears
            self.got_face = True
            self.human_tracked = value[1][0][1][2] if value[1][0][1][2] != '' else 'stranger'
            self.say("I see you, " + self.human_tracked + ".")

            print "face detected"

    def observeHuman(self):
        # human have spoken within t seconds threshold
        print "human observed"

    def on_stop(self):
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
