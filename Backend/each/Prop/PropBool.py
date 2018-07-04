from each.Prop.PropBase import PropBase

from sqlalchemy import Column, Boolean
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class PropBool(PropBase, Base):
    __tablename__ = 'each_prop_bool'
    value = Column(Boolean)

    def __init__(self, eachid, propid, value):
        super().__init__(eachid, propid, value)
