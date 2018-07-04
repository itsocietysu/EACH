import time
import datetime

from sqlalchemy import Column, Boolean, Integer, Date, Sequence
from sqlalchemy.ext.declarative import declarative_base

from each.db import DBConnection

from each.Entities.EntityBase import EntityBase

Base = declarative_base()

class EntityFollow(EntityBase, Base):
    __tablename__ = 'each_follow'

    eachid = Column(Integer, primary_key=True)
    followingid = Column(Integer, primary_key=True)
    permit = Column(Integer)
    is_user = Column(Boolean)
    created = Column(Date)

    json_serialize_items_list = ['eachid', 'followingid', 'permit', 'is_user', 'created']

    def __init__(self, eachid, followingid, permit, is_user):
        super().__init__()

        self.eachid = eachid
        self.followingid = followingid
        self.permit = permit
        self.is_user = is_user

        ts = time.time()
        self.created = self.updated = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')

    @classmethod
    def smart_delete(cls, eachid, followingid):
        with DBConnection() as session:
            res = session.db.query(cls).filter_by(eachid=eachid, followingid=followingid).all()

            if len(res):
                [session.db.delete(_) for _ in res]
                session.db.commit()
            else:
                raise FileNotFoundError('%s was not found' % cls.__name__)

    @classmethod
    def update(cls, eachid, followingid, permit):
        with DBConnection() as session:
            res = session.db.query(cls).filter_by(eachid=eachid, followingid=followingid).all()

            if len(res):
                for _ in res:
                    _.permit = permit
                session.db.commit()
            else:
                raise FileNotFoundError('%s was not found' % cls.__name__)
