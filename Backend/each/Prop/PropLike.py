from sqlalchemy.ext.declarative import declarative_base

from each.Entities.EntityLike import EntityLike
from each.Prop.PropBase import PropBase

Base = declarative_base()

from each.db import DBConnection

class PropLike(PropBase, Base):
    __tablename__ = 'each_prop_like'

    def __init__(self, eachid, propid, value):
        super().__init__(eachid, propid, value)

    @classmethod
    def get_object_property(cls, eachid, propid):
        with DBConnection() as session:
            return [_[1].to_dict() for _ in session.db.query(cls, EntityLike).
                filter(cls.eachid == eachid).
                filter(cls.propid == propid).
                filter(cls.value == EntityLike.eachid).all()]

    @classmethod
    def get_post_user_related(cls, eachid, propid, userid):
        with DBConnection() as session:
            return [_[1].to_dict() for _ in session.db.query(cls, EntityLike).
                filter(cls.eachid == eachid).
                filter(cls.propid == propid).
                filter(cls.value == EntityLike.eachid).
                filter(EntityLike.userid == userid).
                all()]
