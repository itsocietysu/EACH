from sqlalchemy.ext.declarative import declarative_base

from each.Entities.EntityMedia import EntityMedia
from each.Prop.PropBase import PropBase

Base = declarative_base()

from each.db import DBConnection

class PropMedia(PropBase, Base):
    __tablename__ = 'each_prop_media'

    def __init__(self, eachid, propid, value):
        super().__init__(eachid, propid, value)

    @classmethod
    def get_object_property(cls, eachid, propid, items=[]):
        with DBConnection() as session:
            return [_[1].to_dict(items) for _ in session.db.query(cls, EntityMedia).
                filter(cls.eachid == eachid).
                filter(cls.propid == propid).
                filter(cls.value == EntityMedia.eachid).all()]
