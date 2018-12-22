from threading import Thread
from database.definition import Experiential, Mental, Social, Identity, \
    SocalProperties, IdentityProperties, upsert
from pony.orm import db_session, commit
import time


class Memory(Thread):

    def __init__(self, awareness):
        super().__init__()
        self.awareness = awareness

    @db_session
    def save_experiential(self, robot_exp):
        exp = Experiential(subject=robot_exp['subject'],
                           target=robot_exp['target'],
                           physicalAct=robot_exp['physicalAct'],
                           speech=robot_exp['speech'],
                           ambiance_agitationLevel=robot_exp['ambianceEmotion']['agitationLevel'],
                           ambiance_calmLevel=robot_exp['ambianceEmotion']['calmLevel'],
                           emotional_anger=robot_exp['emotionalState'][0],
                           emotional_fear=robot_exp['emotionalState'][1],
                           emotional_joy=robot_exp['emotionalState'][2],
                           emotional_sadness=robot_exp['emotionalState'][3],
                           emotional_analytical=robot_exp['emotionalState'][4],
                           emotional_confident=robot_exp['emotionalState'][5],
                           emotional_tentative=robot_exp['emotionalState'][6],
                           place_lat=robot_exp['place'][0],
                           place_lng=robot_exp['place'][1],
                           exp_datetime=robot_exp['datetime'])
        commit()

    @db_session
    def update_social_prop(self, props):
        """
        props = {
            'person': Social(name='junjie'),
            'property_name': 'age',
            'property_type': 'int',
            'property_value_int': 25
        }
        """
        upsert(SocalProperties, props)
        commit()

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
