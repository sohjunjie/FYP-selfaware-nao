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

        self.memory = ALProxy("ALMemory", cf.ROBOT_IP, cf.ROBOT_PORT)
        self.memory.subscribeToEvent("FaceDetected",
                                     "stimuliEventWatcher",
                                     "onFaceDetected")

        self.tts = ALProxy("ALTextToSpeech", cf.ROBOT_IP, cf.ROBOT_PORT)
        self.got_face = False
        self.human = None

    def say(self, msg):
        self.tts.say(msg)

    def onFaceDetected(self, key, value, msg):
        if value == []:  # empty value when the face disappears
            self.got_face = False
            self.human = None
        elif not self.got_face:  # only speak the first time a face appears
            self.got_face = True
            self.human = value[1][0][1][2] if value[1][0][1][2] != '' else 'stranger'
            self.say("Hello " + self.human + "!")

            # First Field = TimeStamp.
            timeStamp = value[0]
            print "TimeStamp is: " + str(timeStamp)

            # Second Field = array of face_Info's.
            faceInfoArray = value[1]
            for j in range( len(faceInfoArray)-1 ):
                faceInfo = faceInfoArray[j]

                # First Field = Shape info.
                faceShapeInfo = faceInfo[0]

                # Second Field = Extra info (empty for now).
                faceExtraInfo = faceInfo[1]

                print "Face Infos :  alpha %.3f - beta %.3f" % (faceShapeInfo[1], faceShapeInfo[2])
                print "Face Infos :  width %.3f - height %.3f" % (faceShapeInfo[3], faceShapeInfo[4])
                print "Face Extra Infos :" + str(faceExtraInfo)


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
        #stop
        basic_awareness.stopAwareness()
        motion.rest()
        event_broker.shutdown()
        sys.exit(0)
