from sqlalchemy.ext.declarative import declarative_base

from each.Entities.EntityComment import EntityComment
from each.Prop.PropBase import PropBase

Base = declarative_base()

from each.db import DBConnection

class PropComment(PropBase, Base):
    __tablename__ = 'each_prop_comment'

    def __init__(self, eachid, propid, value):
        super().__init__(eachid, propid, value)

    @classmethod
    def get_object_property(cls, eachid, propid):
        with DBConnection() as session:
            return [_[1].to_dict() for _ in session.db.query(cls, EntityComment).
                filter(cls.eachid == eachid).
                filter(cls.propid == propid).
                filter(cls.value == EntityComment.eachid).all()]
