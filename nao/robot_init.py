import logging
import json
import sys
import time
import threading
from naoqi import ALProxy, ALBroker, ALModule
import config as cf


# Global variable to store the stimuliEventWatcher module instance
stimuliEventWatcher = None


class WorldStimuliEventWatcher(ALModule):
    """ A module to react to world stimuli """

    def __init__(self):
        ALModule.__init__(self, "stimuliEventWatcher")

        self.dialog = ALProxy('ALDialog', cf.ROBOT_IP, cf.ROBOT_PORT)
        self.dialog.setLanguage("English")

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

    def say(self, msg):
        self.tts.say(msg)

    def onHumanTracked(self, key, value, msg):
        """ callback for event HumanTracked """
        self.is_human_tracked = True
        self.stop_sound_detection()
        logging.info("got HumanTracked: detected person with ID:" + str(value))
        self.say("Hello there.")
        if value >= 0:  # found a new person
            position_human = self.get_people_perception_data(value)
            expression_human = self.get_people_expression_data(value)
            [x, y, z] = position_human
            print "The tracked person with ID", value, "is at the position:", \
                "x=", x, "/ y=",  y, "/ z=", z

    def onHumanLost(self, key, value, msg):
        """ callback for event HumanLost """
        self.is_human_tracked = False
        logging.info("got HumanLost: lost human" + str(value))
        self.stop_sound_detection()
        self.start_sound_detection()

    def onFaceDetected(self, key, value, msg):
        print "key:", str(key), " value:", str(value)
        self.tts.say('hello stranger')
        self.start_sound_detection()

    def onDialogDetected(self, key, value, msg):
        self.tts.say(value)
        logging.info("heard:" + value)

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
        if self.is_dialog_detection_started::
            self.memory.unsubscribeToEvent("Dialog/LastInput", "stimuliEventWatcher")
            self.is_dialog_detection_started = False

    def get_people_perception_data(self, id_person_tracked):
        self.memory = ALProxy("ALMemory", cf.ROBOT_IP, cf.ROBOT_PORT)
        memory_key = "PeoplePerception/Person/" + str(id_person_tracked) + \
                     "/PositionInWorldFrame"
        return self.memory.getData(memory_key)

    def get_people_expression_data(self, id_person_tracked):
        self.memory = ALProxy("ALMemory", cf.ROBOT_IP, cf.ROBOT_PORT)
        memory_key = "PeoplePerception/Person/" + str(id_person_tracked) + \
                     "/ExpressionProperties"
        return self.memory.getData(memory_key)


if __name__ == "__main__":
    cf.init()
    event_broker = ALBroker("event_broker", "0.0.0.0", 0, cf.cf.ROBOT_IP, cf.cf.ROBOT_PORT)
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
        #stop
        basic_awareness.stopAwareness()
        motion.rest()
        event_broker.shutdown()
        sys.exit(0)
