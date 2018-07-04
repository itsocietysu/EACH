from collections import OrderedDict

from sqlalchemy import Column, Boolean, Integer

from each.db import DBConnection

class PropBase:
    eachid = Column(Integer, primary_key=True)
    propid = Column(Integer, primary_key=True)
    value = Column(Integer)

    def to_dict(self):
        res = OrderedDict([(key, self.__dict__[key]) for key in ['eachid', 'propid', 'value']])
        return res

    def __init__(self, eachid, propid, value):
        self.eachid = eachid
        self.propid = propid
        self.value = value

    def add(self, session=None, no_commit=False):
        def proseed(session):
            session.db.add(self)
            if not no_commit:
                session.db.commit()
                return self.eachid
            return None

        if session:
            return proseed(session)

        with DBConnection() as session:
            return proseed(session)

        return None

    def update(self, session, no_commit=False):
        def proseed(session):
            entities = self.__class__.get().filter_by(eachid=self.eachid, propid=self.propid).all()
            for _ in entities:
                _.value = self.value

            if not no_commit:
                session.db.commit()

        if session:
            proseed(session)

        with DBConnection() as session:
            proseed(session)

    @classmethod
    def delete(cls, eachid, propid, raise_exception=True):
        with DBConnection() as session:
            res = session.db.query(cls).filter_by(eachid=eachid, propid=propid).all()

            if len(res):
                [session.db.delete(_) for _ in res]
                session.db.commit()
            else:
                if raise_exception:
                    raise FileNotFoundError('(eachid, propid)=(%i, %i) was not found' % (eachid, propid))

    @classmethod
    def delete_value(cls, value, raise_exception=True):
        with DBConnection() as session:
            res = session.db.query(cls).filter_by(value=value).all()

            if len(res):
                [session.db.delete(_) for _ in res]
                session.db.commit()
            else:
                if raise_exception:
                    raise FileNotFoundError('(value)=(%s) was not found' % str(value))

    @classmethod
    def get(cls):
        with DBConnection() as session:
            return session.db.query(cls)

    @classmethod
    def get_object_property(cls, eachid, propid):
        with DBConnection() as session:
            return [_.value for _ in session.db.query(cls).filter_by(eachid=eachid, propid=propid).all()]
