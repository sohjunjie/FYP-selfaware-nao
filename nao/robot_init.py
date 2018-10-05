import logging
import json
import sys
import time
import threading
from naoqi import ALProxy, ALBroker, ALModule
import config as cf


# Global variable to store the stimuliEventWatcher module instance
global stimuliEventWatcher


class WorldStimuliEventWatcher(ALModule):
    """ A module to react to world stimuli """

    def __init__(self):
        ALModule.__init__(self, "stimuliEventWatcher")

        self.asr = ALProxy("ALSpeechRecognition", cf.ROBOT_IP, cf.ROBOT_PORT)
        self.asr.setLanguage("English")
        # self.asr.pause(True)
        # with open('dictionary.txt') as f:
        #     self.asr.setVocabulary(['hello', 'robot', 'cool'], False)
        # self.asr.pause(False)

        self.dialog = ALProxy('ALDialog', cf.ROBOT_IP, cf.ROBOT_PORT)
        self.dialog.setLanguage("English")
        self.dialog_topic = self.dialog.loadTopic('/var/persistent/home/nao/HumanDialog/HumanDialog_enu.top')
        self.dialog.subscribe('myModule')
        self.dialog.activateTopic(self.dialog_topic)

        self.memory = ALProxy("ALMemory", cf.ROBOT_IP, cf.ROBOT_PORT)
        self.memory.subscribeToEvent("ALBasicAwareness/HumanTracked",
                                     "stimuliEventWatcher",
                                     "onHumanTracked")
        self.memory.subscribeToEvent("ALBasicAwareness/HumanLost",
                                     "stimuliEventWatcher",
                                     "onHumanLost")
        self.memory.subscribeToEvent("ALSoundLocalization/SoundLocated",
                                     "stimuliEventWatcher",
                                     "onSoundLocated")
        self.memory.subscribeToEvent("FaceDetected",
                                     "stimuliEventWatcher",
                                     "onFaceDetected")

        self.tts = ALProxy("ALTextToSpeech", cf.ROBOT_IP, cf.ROBOT_PORT)
        self.is_sound_detection_started = True
        self.is_human_tracked = False
        self.is_dialog_detection_started = False
        self.got_face = False
        self.human_tracked = None

    def say(self, msg):
        self.tts.say(msg)

    def onHumanTracked(self, key, value, msg):
        """ callback for event HumanTracked """
        self.is_human_tracked = True
        self.stop_sound_detection()
        self.start_dialog_detection()
        if value >= 0:
            logging.info("got HumanTracked: detected person with ID:" + str(value))

    def onHumanLost(self, key, value, msg):
        """ callback for event HumanLost """
        self.is_human_tracked = False
        self.human_tracked = None
        logging.info("got HumanLost: lost human" + str(value))
        self.stop_dialog_detection()
        self.start_sound_detection()

    def onFaceDetected(self, key, value, msg):
        if value == []:  # empty value when the face disappears
            self.got_face = False
            self.human_tracked = None
        elif not self.got_face:  # only speak the first time a face appears
            self.got_face = True
            self.human_tracked = value[1][0][1][2] if value[1][0][1][2] != '' else 'stranger'
            self.say("I see you, " + self.human_tracked + ".")

    def onDialogDetected(self, key, value, msg):
        if not value:
            return
        self.stop_dialog_detection()
        if self.got_face and self.human_tracked:
            self.say(self.human_tracked + ", you said " + value)
            logging.info("heard: " + value)
        self.start_dialog_detection()

    def onSoundLocated(self, key, value, msg):
        self.tts.say("I heard something.")
        # print "sound detected at position=", value

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


if __name__ == "__main__":
    cf.init()
    event_broker = ALBroker("event_broker", "0.0.0.0", 0, cf.ROBOT_IP, cf.ROBOT_PORT)
    global stimuliEventWatcher
    stimuliEventWatcher = WorldStimuliEventWatcher()
    basic_awareness = ALProxy("ALBasicAwareness", cf.ROBOT_IP, cf.ROBOT_PORT)
    motion = ALProxy("ALMotion", cf.ROBOT_IP, cf.ROBOT_PORT)

    #start
    motion.wakeUp()
    basic_awareness.setEngagementMode("FullyEngaged")
    basic_awareness.startAwareness()

    #loop on, wait for events until interruption
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print "Interrupted by user, shutting down"
        stimuliEventWatcher.on_stop()
        basic_awareness.stopAwareness()
        motion.rest()
        event_broker.shutdown()
        sys.exit(0)
