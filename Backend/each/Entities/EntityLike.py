import datetime
import time

from sqlalchemy import Column, Date, Integer, Sequence
from sqlalchemy.ext.declarative import declarative_base

from each.Entities.EntityBase import EntityBase
from each.Entities.EntityProp import EntityProp

from each.db import DBConnection

Base = declarative_base()

class EntityLike(EntityBase, Base):
    __tablename__ = 'each_like'

    eachid = Column(Integer, Sequence('each_seq'), primary_key=True)
    userid = Column(Integer)
    created = Column(Date)
    weight = Column(Integer)

    json_serialize_items_list = ['eachid', 'userid', 'created', 'weight']

    def __init__(self, userid, weight):
        super().__init__()

        self.userid = userid
        ts = time.time()
        self.created = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')
        self.weight = weight

    @classmethod
    def add_from_json(cls, data, userId):
        PROPNAME_MAPPING = EntityProp.map_name_id()

        _id = None
        if 'weight' in data and 'eachid' in data:
            weight = data['weight']
            eachid = data['eachid']

            from each.Prop.PropLike import PropLike
            likes = PropLike.get_post_user_related(eachid, PROPNAME_MAPPING['like'], userId)


            if len(likes):
                for _ in likes:
                    EntityLike.delete(_['eachid'])
                    PropLike.delete_value(_['eachid'], raise_exception=False)

            new_entity = EntityLike(userId, weight)
            _id = new_entity.add()

            PropLike(eachid, PROPNAME_MAPPING['like'], _id).add()

        return _id


    @classmethod
    def update_from_json(cls, data):
        eachid = None

        if 'id' in data:
            with DBConnection() as session:
                eachid = data['id']
                entity = session.db.query(EntityLike).filter_by(eachid=eachid).all()

                if len(entity):
                    for _ in entity:
                        if 'weight' in data:
                            _.weight = data['weight']

                        session.db.commit()

        return eachid
