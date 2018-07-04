from collections import OrderedDict
import datetime
import time

from sqlalchemy import Column, String, Integer, Date, Sequence
from sqlalchemy.ext.declarative import declarative_base

from each.Entities.EntityBase import EntityBase
from each.Entities.EntityProp import EntityProp

from each.Prop.PropBool import PropBool
from each.Prop.PropReal import PropReal
from each.Prop.PropMedia import PropMedia
from each.Prop.PropLike import PropLike
from each.Prop.PropLocation import PropLocation
from each.db import DBConnection

Base = declarative_base()

class EntityCourt(EntityBase, Base):
    __tablename__ = 'each_court'

    eachid = Column(Integer, Sequence('each_seq'), primary_key=True)
    ownerid = Column(Integer)
    name = Column(String)
    desc = Column(String)
    created = Column(Date)
    updated = Column(Date)

    json_serialize_items_list = ['eachid', 'ownerid', 'name', 'desc', 'created', 'updated']

    def __init__(self, ownerid, name, desc):
        super().__init__()

        self.ownerid = ownerid
        self.name = name
        self.desc = desc

        ts = time.time()
        self.created = self.updated = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')

    @classmethod
    def add_from_json(cls, data):
        PROPNAME_MAPPING = EntityProp.map_name_id()

        eachid = None

        PROP_MAPPING = {
            'private':
                lambda session, _eachid, _id, _value, _uid: PropBool(_eachid, _id, _value)
                    .add(session=session, no_commit=True),
            'isopen':
                lambda session, _eachid, _id, _value, _uid: PropBool(_eachid, _id, _value)
                    .add(session=session, no_commit=True),
            'isfree':
                lambda session, _eachid, _id, _value, _uid: PropBool(_eachid, _id, _value)
                    .add(session=session, no_commit=True),
            'isonair':
                lambda session, _eachid, _id, _value, _uid: PropBool(_eachid, _id, _value)
                    .add(session=session, no_commit=True),
            'price':
                lambda session, _eachid, _id, _value, _uid: PropReal(_eachid, _id, _value)
                    .add(session=session, no_commit=True),
            'location':
                lambda s, _eachid, _id, _val, _uid: PropLocation(_eachid, _id, _val)
                    .add(session=s, no_commit=True),
            'media':
                lambda s, _eachid, _id, _val, _uid: [cls.process_media(s, 'image', _uid, _eachid, _id, _)
                                                    for _ in _val],
            'equipment':
                lambda s, _eachid, _id, _val, _uid: [cls.process_media(s, 'equipment', _uid, _eachid, _id, _)
                                                    for _ in _val]
        }

        if 'ownerid' in data and 'name' in data and 'desc' in data and 'prop' in data :
            ownerid = data['ownerid']
            name = data['name']
            desc = data['desc']

            new_entity = EntityCourt(ownerid, name, desc)
            eachid = new_entity.add()

            with DBConnection() as session:
                for prop_name, prop_val in data['prop'].items():
                    if prop_name in PROPNAME_MAPPING and prop_name in PROP_MAPPING:
                        PROP_MAPPING[prop_name](session, eachid, PROPNAME_MAPPING[prop_name], prop_val, ownerid)
                    else:
                        new_entity.delete(eachid)
                        raise Exception('{%s} not existed property\nPlease use one of:\n%s' %
                                        (prop_name, str(PROPNAME_MAPPING)))

                session.db.commit()

        return eachid

    @classmethod
    def get_wide_object(cls, eachid, items=[]):
        PROPNAME_MAPPING = EntityProp.map_name_id()

        PROP_MAPPING = {
            'private':   lambda _eachid, _id: PropBool.get_object_property(_eachid, _id),
            'isopen':    lambda _eachid, _id: PropBool.get_object_property(_eachid, _id),
            'isfree':    lambda _eachid, _id: PropBool.get_object_property(_eachid, _id),
            'isonair':   lambda _eachid, _id: PropBool.get_object_property(_eachid, _id),
            'price':     lambda _eachid, _id: PropReal.get_object_property(_eachid, _id),
            'location':  lambda _eachid, _id: PropLocation.get_object_property(_eachid, _id),
            'media':     lambda _eachid, _id: PropMedia.get_object_property(_eachid, _id),
            'equipment': lambda _eachid, _id: PropMedia.get_object_property(_eachid, _id),
            'like':      lambda _eachid, _id: PropLike.get_object_property(_eachid, _id)
        }

        result = {
            'eachid': eachid
        }
        for key, propid in PROPNAME_MAPPING.items():
            if key in PROP_MAPPING and (not len(items) or key in items):
                result.update({key: PROP_MAPPING[key](eachid, propid)})

        return result

    @classmethod
    def delete_wide_object(cls, eachid):
        PROPNAME_MAPPING = EntityProp.map_name_id()

        PROP_MAPPING = {
            'private':   lambda _eachid, _id: PropBool.delete(_eachid, _id, False),
            'isopen':    lambda _eachid, _id: PropBool.delete(_eachid, _id, False),
            'isfree':    lambda _eachid, _id: PropBool.delete(_eachid, _id, False),
            'isonair':   lambda _eachid, _id: PropBool.delete(_eachid, _id, False),
            'price':     lambda _eachid, _id: PropReal.delete(_eachid, _id, False),
            'location':  lambda _eachid, _id: PropLocation.delete(_eachid, _id, False),
            'media':     lambda _eachid, _id: PropMedia.delete(_eachid, _id, False),
            'equipment': lambda _eachid, _id: PropMedia.delete(_eachid, _id, False)
        }

        for key, propid in PROPNAME_MAPPING.items():
            if key in PROP_MAPPING:
                PROP_MAPPING[key](eachid, propid)
