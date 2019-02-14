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

        # self.asr = ALProxy("ALSpeechRecognition", cf.ROBOT_IP, cf.ROBOT_PORT)
        # self.asr.setLanguage("English")

        self.dialog = ALProxy('ALDialog', cf.ROBOT_IP, cf.ROBOT_PORT)
        self.dialog.setLanguage("English")

        self.dialog_topic = self.dialog.loadTopic('/var/persistent/home/nao/HumanDialog/HumanDialog_enu.top')
        self.dialog.subscribe('myModule')
        self.dialog.activateTopic(self.dialog_topic)

        self.memory = ALProxy("ALMemory", cf.ROBOT_IP, cf.ROBOT_PORT)

        self.tts = ALProxy("ALTextToSpeech", cf.ROBOT_IP, cf.ROBOT_PORT)
        self.is_dialog_detection_started = False
        if not self.is_dialog_detection_started:
            print 'starting dialog detection'
            try:
                self.memory.subscribeToEvent("Dialog/LastInput",
                                            "stimuliEventWatcher",
                                            "onDialogDetected")
            except RuntimeError:
                print "DL already started"
            self.is_dialog_detection_started = True

    def say(self, msg):
        self.tts.say(msg)

    def onDialogDetected(self, key, value, msg):
        self.tts.say(value)
        print '1' + key, '2' + value, '3' + msg
        logging.info("heard:" + value)

    def stop_dialog_detection(self):
        if self.is_dialog_detection_started:
            self.memory.unsubscribeToEvent("Dialog/LastInput", "stimuliEventWatcher")
            self.is_dialog_detection_started = False


if __name__ == "__main__":
    event_broker = ALBroker("event_broker", "0.0.0.0", 0, cf.ROBOT_IP, cf.ROBOT_PORT)
    stimuliEventWatcher = WorldStimuliEventWatcher()
    # basic_awareness = ALProxy("ALBasicAwareness", cf.ROBOT_IP, cf.ROBOT_PORT)
    # motion = ALProxy("ALMotion", cf.ROBOT_IP, cf.ROBOT_PORT)

    #start
    # motion.wakeUp()
    # basic_awareness.setEngagementMode("FullyEngaged")
    # basic_awareness.startAwareness()

    #loop on, wait for events until interruption
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print "Interrupted by user, shutting down"
        #stop
        stimuliEventWatcher.dialog.unsubscribe('myModule')
        stimuliEventWatcher.dialog.deactivateTopic(stimuliEventWatcher.dialog_topic)
        stimuliEventWatcher.dialog.unloadTopic(stimuliEventWatcher.dialog_topic)
        stimuliEventWatcher.motion.rest()
        event_broker.shutdown()
        sys.exit(0)
