from database.definition import Experiential, Mental, Social, Identity, \
    SocalProperties, IdentityProperties, upsert
from pony.orm import db_session, commit, select
from datetime import datetime as dt
from datetime import timedelta as td

class Memory():

    def __init__(self, awareness):
        super().__init__()
        self.awareness = awareness

    @db_session
    def save_experiential(self, robot_exp):
        if self.awareness.exeProc.dialogueManager.context['__conversation_id'] is None:
            conv_id = 0
            try:
                conv_id = select(exp.conversation_id for exp in Experiential).max() + 1
            except:
                pass
            self.awareness.exeProc.dialogueManager.context['__conversation_id'] = conv_id

        context_conv_id = self.awareness.exeProc.dialogueManager.context['__conversation_id']
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
                           exp_datetime=robot_exp['datetime'],
                           conversation_id=context_conv_id)
        commit()

    @db_session
    def update_social_prop(self, person_name, props, set=None):
        """
        props = {
            'person': Social(name='junjie'),
            'property_name': 'age',
            'property_type': 'int',
            'property_value_int': 25
        }
        """

        persons = select(p for p in Social if
                    p.name == person_name
                 )[:1]
        
        if len(persons) == 0:
            return False

        person = persons[0]
        props['person'] = person
        sp = upsert(SocalProperties, props, set=set)
        commit()

        return sp

    @db_session
    def have_met_before(self, human):
        """
        Determine if robot has met human before by querying
        the experiential aspect
        """

        context_conv_id = self.awareness.exeProc.dialogueManager.context['__conversation_id']
        if context_conv_id is None:
            return False

        q = select(e for e in Experiential if
                e.conversation_id < context_conv_id
            )[:1]
        return len(q) > 0

    @db_session
    def get_robot_name(self):
        q = select(i for i in Identity)[:1]
        return q[0].name

    @db_session
    def query_robot(self, prop_name):

        idProps = select(ip for ip in IdentityProperties if 
                    ip.property_name == prop_name
                  )[:1]

        if len(idProps) == 0:
            return ''
        idProp = idProps[0]

        if idProp.property_type == 'str':
            return idProp.property_value_str
        if idProp.property_type == 'int':
            return str(idProp.property_value_int)
        if idProp.property_type == 'float':
            return str(idProp.property_value_float)
        if idProp.property_type == 'datetime':
            return str(idProp.property_value_datetime)
        if idProp.property_type == 'decimal':
            return str(idProp.property_value_decimal)
        if idProp.property_type == 'bool':
            return str(idProp.property_value_bool)

        return ''


    @db_session
    def query_human(self, human_name, prop_name):
        
        socialHuman = select(s for s in Social if s.name == human_name)[:1]

        if len(socialHuman) == 0:
            return ''

        socialProps = select(sp for sp in SocalProperties if 
                    sp.person == socialHuman[0] and
                    sp.property_name == prop_name
                  )[:1]

        if len(socialProps) == 0:
            return ''

        socialProp = socialProps[0]
        if socialProp.property_type == 'str':
            return socialProp.property_value_str
        if socialProp.property_type == 'int':
            return str(socialProp.property_value_int)
        if socialProp.property_type == 'float':
            return str(socialProp.property_value_float)
        if socialProp.property_type == 'datetime':
            return str(socialProp.property_value_datetime)
        if socialProp.property_type == 'decimal':
            return str(socialProp.property_value_decimal)
        if socialProp.property_type == 'bool':
            return str(socialProp.property_value_bool)

        return ''
