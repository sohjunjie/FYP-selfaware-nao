from naoqi import ALProxy, ALBroker, ALModule
# from websocket import create_connection
import time
import sys
import speech_recognition as sr

ip_robot = "127.0.0.1"
port_robot = 9559
prompt_path = '/home/nao/recordings/microphones/siri1.wav'
prompt_endp = '/home/nao/recordings/microphones/siri2.wav'
record_path = '/home/nao/recordings/microphones/temp.wav'

# Global variable to store the stimuliEventWatcher module instance
stimuliEventWatcher = None
memory = None


class WorldStimuliEventWatcher(ALModule):
    """ A module to react to world stimuli """

    def __init__(self):
        ALModule.__init__(self, "stimuliEventWatcher")
        global memory
        memory = ALProxy("ALMemory", ip_robot, port_robot)
        memory.subscribeToEvent("ALBasicAwareness/HumanTracked",
                                "stimuliEventWatcher",
                                "onHumanTracked")
        memory.subscribeToEvent("ALBasicAwareness/HumanLost",
                                "stimuliEventWatcher",
                                "onHumanLost")
        memory.subscribeToEvent("ALSoundLocalization/SoundLocated",
                                "stimuliEventWatcher",
                                "onSoundLocated")
        memory.subscribeToEvent("TouchChanged",
                                "stimuliEventWatcher",
                                "onTouched")

        # self.speech_reco = ALProxy("ALSpeechRecognition", ip_robot, port_robot)
        self.audio_reco = ALProxy("ALAudioRecorder", ip_robot, port_robot)
        self.audio_play = ALProxy("ALAudioPlayer", ip_robot, port_robot)
        self.tts = ALProxy("ALTextToSpeech", ip_robot, port_robot)
        self.is_speech_reco_started = False
        self.is_sound_detection_started = True
        try:
            pass
            # self.pc_ws = create_connection("ws://192.168.0.254:8888/ws")
        except:
            pass

    def say(self, msg):
        if self.is_speech_reco_started:
            self.stop_speech_reco()
            self.tts.say(msg)
            self.start_speech_reco()
        else:
            self.tts.say(msg)

    def onHumanTracked(self, key, value, msg):
        self.stop_sound_detection()
        """ callback for event HumanTracked """
        print "got HumanTracked: detected person with ID:", str(value)
        self.say("Hello there.")
        if value >= 0:  # found a new person
            # self.start_speech_reco()
            position_human = self.get_people_perception_data(value)
            expression_human = self.get_people_expression_data(value)
            [x, y, z] = position_human
            print "The tracked person with ID", value, "is at the position:", \
                "x=", x, "/ y=",  y, "/ z=", z

    def onHumanLost(self, key, value, msg):
        """ callback for event HumanLost """
        print "got HumanLost: lost human", str(value)
        # self.stop_speech_reco()
        self.start_sound_detection()

    def onSoundLocated(self, key, value, msg):
        self.tts.say("I heard something.")
        # print "sound detected at position=", value

    def onTouched(self, strVarName, value):
        if value[0][0] == 'Head':
            memory.unsubscribeToEvent("TouchChanged", "stimuliEventWatcher")

            self.is_speech_reco_started = not self.is_speech_reco_started
            if self.is_speech_reco_started is False:
                self.audio_reco.stopMicrophonesRecording()
                self.audio_play.playFile(prompt_endp, 0.7, 0)
                time.sleep(0.1)

                r = sr.Recognizer()
                with sr.WavFile(record_path) as source:
                    audio = r.record(source)
                print "You said: " + r.recognize_google(audio)

            else:
                self.audio_play.playFile(prompt_path, 0.7, 0)
                self.audio_reco.startMicrophonesRecording(record_path, 'wav', 16000, (0,0,1,0))

            try:
                memory.subscribeToEvent("TouchChanged",
                                        "stimuliEventWatcher",
                                        "onTouched")
            except RuntimeError:
                print "TC already started"

    def start_sound_detection(self):
        if not self.is_sound_detection_started:
            try:
                memory.subscribeToEvent("ALSoundLocalization/SoundLocated",
                                        "stimuliEventWatcher",
                                        "onSoundLocated")
            except RuntimeError:
                print "ASL already started"
            self.is_sound_detection_started = True

    def stop_sound_detection(self):
        if self.is_sound_detection_started:
            memory.unsubscribeToEvent("ALSoundLocalization/SoundLocated", "stimuliEventWatcher")
            self.is_sound_detection_started = False

    def get_people_perception_data(self, id_person_tracked):
        memory = ALProxy("ALMemory", ip_robot, port_robot)
        memory_key = "PeoplePerception/Person/" + str(id_person_tracked) + \
                     "/PositionInWorldFrame"
        return memory.getData(memory_key)

    def get_people_expression_data(self, id_person_tracked):
        memory = ALProxy("ALMemory", ip_robot, port_robot)
        memory_key = "PeoplePerception/Person/" + str(id_person_tracked) + \
                     "/ExpressionProperties"
        return memory.getData(memory_key)

    def start_speech_reco(self):
        """ start asr when someone's detected in event handler class """
        if not self.is_speech_reco_started:
            try:
                self.speech_reco.setVocabulary([], True)
            except RuntimeError:
                print "ASR already started"
            self.speech_reco.setVisualExpression(True)
            self.speech_reco.subscribe("BasicAwareness_Test")
            self.is_speech_reco_started = True
            print "start ASR"

    def stop_speech_reco(self):
        """ stop asr when someone's detected in event handler class """
        if self.is_speech_reco_started:
            self.speech_reco.unsubscribe("BasicAwareness_Test")
            self.is_speech_reco_started = False
            print "stop ASR"


if __name__ == "__main__":
    event_broker = ALBroker("event_broker", "0.0.0.0", 0, ip_robot, port_robot)
    global stimuliEventWatcher
    stimuliEventWatcher = WorldStimuliEventWatcher()
    basic_awareness = ALProxy("ALBasicAwareness", ip_robot, port_robot)
    motion = ALProxy("ALMotion", ip_robot, port_robot)

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
