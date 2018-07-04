from collections import OrderedDict
import datetime
import time

from sqlalchemy import Column, String, Integer, Date, Sequence
from sqlalchemy.ext.declarative import declarative_base

from each.Entities.EntityBase import EntityBase
from each.Entities.EntityProp import EntityProp

from each.Prop.PropLocation import PropLocation
from each.Prop.PropComment import PropComment
from each.Prop.PropLike import PropLike
from each.Prop.PropMedia import PropMedia

from each.db import DBConnection

Base = declarative_base()


class EntityPost(EntityBase, Base):
    __tablename__ = 'each_post'

    eachid = Column(Integer, Sequence('each_seq'), primary_key=True)
    userid = Column(Integer)
    description = Column(String)
    created = Column(Date)
    updated = Column(Date)

    json_serialize_items_list = ['eachid', 'userid', 'description', 'created', 'updated']

    def __init__(self, userid, description):
        super().__init__()

        self.userid = userid
        self.description = description

        ts = time.time()
        self.created = self.updated = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')

    @classmethod
    def add_from_json(cls, data, userId):
        eachid = None

        if userId is None:
            return None

        PROPNAME_MAPPING = EntityProp.map_name_id()

        PROP_MAPPING = {
            'location':
                lambda s, _eachid, _id, _val, _uid: PropLocation(_eachid, _id, _val).add(session=s, no_commit=True),
            'comment':
                lambda s, _eachid, _id, _val, _uid: [PropComment(_eachid, _id, _)
                                                        .add(session=s, no_commit=True) for _ in _val],
            'media':
                lambda s, _eachid, _id, _val, _uid: [cls.process_media(s, 'image', _uid, _eachid, _id, _) for _ in _val],
            'like':
                lambda s, _eachid, _id, _val, _uid: [PropLike(_eachid, _id, _)
                                                        .add(session=s, no_commit=True) for _ in _val]
        }

        if 'description' in data and "prop" in data:
            description = data['description']

            new_entity = EntityPost(userId, description)
            eachid = new_entity.add()

            with DBConnection() as session:
                for prop_name, prop_val in data['prop'].items():

                    if prop_name in PROPNAME_MAPPING and prop_name in PROP_MAPPING:
                        PROP_MAPPING[prop_name](session, eachid, PROPNAME_MAPPING[prop_name], prop_val, userId)
                    else:
                        new_entity.delete(eachid)
                        raise Exception('{%s} not existed property\nPlease use one of:\n%s' %
                                        (prop_name, str(PROPNAME_MAPPING)))

                from each.Prop.PropPost import PropPost
                PropPost(userId, PROPNAME_MAPPING["post"], eachid).add(session, no_commit=True)
                session.db.commit()

        return eachid

    @classmethod
    def update_from_json(cls, data):
        eachid = None

        if 'id' in data:
            with DBConnection() as session:
                eachid = data['id']
                entity = session.db.query(EntityPost).filter_by(eachid=eachid).all()

                if len(entity):
                    for _ in entity:
                        if 'description' in data:
                            _.description = data['description']

                        session.db.commit()

        return eachid

    @classmethod
    def get_wide_object(cls, eachid, items=[]):
        PROPNAME_MAPPING = EntityProp.map_name_id()

        PROP_MAPPING = {
            'location': lambda _eachid, _id: PropLocation.get_object_property(_eachid, _id),
            'comment':  lambda _eachid, _id: PropComment.get_object_property(_eachid, _id),
            'media':    lambda _eachid, _id: PropMedia.get_object_property(_eachid, _id, ['eachid', 'url']),
            'like':     lambda _eachid, _id: PropLike.get_object_property(_eachid, _id)
        }

        result = {
            'eachid': eachid,
        }
        for key, propid in PROPNAME_MAPPING.items():
            if key in PROP_MAPPING and (not len(items) or key in items):
                result.update({key: PROP_MAPPING[key](eachid, propid)})

        return result

    @classmethod
    def delete_wide_object(cls, eachid):
        PROPNAME_MAPPING = EntityProp.map_name_id()

        PROP_MAPPING = {
            'location': lambda _eachid, _id: PropLocation.delete(_eachid, _id, False),
            'comment':  lambda _eachid, _id: PropComment.delete(_eachid, _id, False),
            'media':    lambda _eachid, _id: PropMedia.delete(_eachid, _id, False),
            'like':     lambda _eachid, _id: PropLike.delete(_eachid, _id, False)
        }

        for key, propid in PROPNAME_MAPPING.items():
            if key in PROP_MAPPING:
                PROP_MAPPING[key](eachid, propid)

        from each.Prop.PropPost import PropPost
        for _ in EntityPost.get().filter_by(eachid=eachid).all():
            PropPost.delete(_.userid, PROPNAME_MAPPING["post"], False)
