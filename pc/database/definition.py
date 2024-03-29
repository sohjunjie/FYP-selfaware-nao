from pony.orm import *
from pony.orm.core import EntityMeta
from datetime import datetime
from decimal import Decimal
# from pony import orm

db = Database()
db.bind(provider='sqlite', filename='database.sqlite', create_db=True)


class Experiential(db.Entity):
    conversation_id = Required(int, default=0)
    subject = Required(str)
    target = Optional(str, nullable=True)
    physicalAct = Required(str)
    speech = Optional(str)
    ambiance_agitationLevel = Required(float)
    ambiance_calmLevel = Required(float)
    emotional_anger = Required(float)
    emotional_fear = Required(float)
    emotional_joy = Required(float)
    emotional_sadness = Required(float)
    emotional_analytical = Required(float)
    emotional_confident = Required(float)
    emotional_tentative = Required(float)
    place_lat = Required(float)
    place_lng = Required(float)
    exp_datetime = Required(datetime)


# class Mental(db.Entity):
#     goal = Required(str)
#     status = Required(str)
#     goal_datetime = Required(datetime)


class Social(db.Entity):
    name = Required(str, unique=True)
    relationship = Required(str)
    identity = Set('SocalProperties')


class Identity(db.Entity):
    name = Required(str, unique=True)
    identity = Set('IdentityProperties')


class SocalProperties(db.Entity):
    property_name = Required(str)
    property_type = Required(str)
    property_value_str = Optional(str)
    property_value_int = Optional(int)
    property_value_float = Optional(float)
    property_value_datetime = Optional(datetime)
    property_value_decimal = Optional(Decimal)
    property_value_bool = Optional(bool)
    created_on = Required(datetime, sql_default='CURRENT_TIMESTAMP')
    updated_on = Required(datetime, sql_default='CURRENT_TIMESTAMP', volatile=True)
    person = Required(Social)


class IdentityProperties(db.Entity):
    """
    robot attribute values:
        (int) age               3
        (str) personality       neutral
        (str) goal              make friends
        (str) interest          make friends
        (str) occupation        robot
        (str) nationality       france
        (str) race              robotic
        (str) religion          free thinker
        (date) birthday         1/10/2015
        (int) birthyear         2015
        (int) birthmonth        october
        (int) birthday          1
        (decimal) wealth        0.00
        (str) name              silva
    """
    property_name = Required(str)
    property_type = Required(str)
    property_value_str = Optional(str)
    property_value_int = Optional(int)
    property_value_float = Optional(float)
    property_value_datetime = Optional(datetime)
    property_value_decimal = Optional(Decimal)
    property_value_bool = Optional(bool)
    person = Required(Identity)


# class Physical(db.Entity):
#     pass


def upsert(cls, get, set=None):
    """
    Interacting with Pony entities.

    :param cls: The actual entity class
    :param get: Identify the object (e.g. row) with this dictionary
    :param set: 
    :return:
    """
    # does the object exist
    assert isinstance(cls, EntityMeta), "{cls} is not a database entity".format(cls=cls)

    # if no set dictionary has been specified
    set = set or {}

    if not cls.exists(**get):
        return cls(**set, **get)
    else:
        # get the existing object
        obj = cls.get(**get)
        for key, value in set.items():
            obj.__setattr__(key, value)
        return obj


@db_session
def populate_database():
    i = Identity(name='silva')
    ip1 = IdentityProperties(property_name='age', property_type='int', property_value_int=3, person=i)
    ip2 = IdentityProperties(property_name='personality', property_type='str', property_value_str='neutral', person=i)
    ip3 = IdentityProperties(property_name='goal', property_type='str', property_value_str='make friends', person=i)
    ip4 = IdentityProperties(property_name='interest', property_type='str', property_value_str='making new friends', person=i)
    ip5 = IdentityProperties(property_name='occupation', property_type='str', property_value_str='companion robot', person=i)
    ip6 = IdentityProperties(property_name='specialization', property_type='str', property_value_str='companionship', person=i)
    ip7 = IdentityProperties(property_name='nationality', property_type='str', property_value_str='french', person=i)
    ip8 = IdentityProperties(property_name='birthplace', property_type='str', property_value_str='france', person=i)
    ip9 = IdentityProperties(property_name='religion', property_type='str', property_value_str='freethinker', person=i)
    ipa = IdentityProperties(property_name='race', property_type='str', property_value_str='robot', person=i)
    ipb = IdentityProperties(property_name='birthdate', property_type='datetime', property_value_datetime=datetime(year=2015, month=10, day=1), person=i)
    ipc = IdentityProperties(property_name='wealth', property_type='decimal', property_value_decimal=0.00, person=i)
    ipd = IdentityProperties(property_name='birthyear', property_type='int', property_value_int=2015, person=i)
    ipe = IdentityProperties(property_name='birthmonth', property_type='str', property_value_str='october', person=i)
    ipf = IdentityProperties(property_name='birthday', property_type='int', property_value_int=1, person=i)
    ipg = IdentityProperties(property_name='name', property_type='str', property_value_str='silva', person=i)

    s = Social(name='john', relationship='friend')
    sp1 = SocalProperties(property_name='age', property_type='int', property_value_int=25, person=s)
    sp2 = SocalProperties(property_name='personality', property_type='str', property_value_str='neutral', person=s)
    sp3 = SocalProperties(property_name='interest', property_type='str', property_value_str='robotics', person=s)
    sp4 = SocalProperties(property_name='occupation', property_type='str', property_value_str='student', person=s)
    sp5 = SocalProperties(property_name='nationality', property_type='str', property_value_str='Singaporean', person=s)
    sp6 = SocalProperties(property_name='birthplace', property_type='str', property_value_str='Singapore', person=s)
    sp7 = SocalProperties(property_name='religion', property_type='str', property_value_str='freethinker', person=s)
    sp8 = SocalProperties(property_name='race', property_type='str', property_value_str='chinese', person=s)
    sp9 = SocalProperties(property_name='birthdate', property_type='datetime', property_value_datetime=datetime(year=1993, month=9, day=17), person=s)
    spa = SocalProperties(property_name='wealth', property_type='decimal', property_value_decimal=10.00, person=s)
    spb = SocalProperties(property_name='birthyear', property_type='int', property_value_int=1993, person=s)
    spc = SocalProperties(property_name='birthmonth', property_type='str', property_value_str='september', person=s)
    spd = SocalProperties(property_name='birthday', property_type='int', property_value_int=17, person=s)
    spe = SocalProperties(property_name='name', property_type='str', property_value_str='john', person=s)

    s1 = Social(name='tom', relationship='friend')
    s1 = Social(name='jack', relationship='friend')

    commit()


db.generate_mapping(create_tables=True)

"""
from database.definition import *
from pony.orm import *
populate_database()
"""

# EXAMPLE CODE
# >>> p1 = Person(name='John', age=20)
# >>> p2 = Person(name='Mary', age=22)
# >>> p3 = Person(name='Bob', age=30)
# >>> c1 = Car(make='Toyota', model='Prius', owner=p2)
# >>> c2 = Car(make='Ford', model='Explorer', owner=p3)
# >>> commit()
