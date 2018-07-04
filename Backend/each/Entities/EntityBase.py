import json
import base64

from collections import OrderedDict

from each.db import DBConnection

from each.MediaResolver.MediaResolverFactory import MediaResolverFactory

class EntityBase:
    host = '.'
    PERMIT_NONE = 0
    PERMIT_ACCESSED = 1
    PERMIT_ADMIN = 2
    PERMIT_OWNER = 2

    json_serialize_items_list = ['']

    MediaCls = None
    MediaPropCls = None

    def to_dict(self, items=[]):
        def fullfill_entity(key, value):
            if key == 'url':
                value = '%s%s' % (EntityBase.host, value[1:])
            return value

        def dictionate_entity(entity):
            try:
                json.dump(entity)
                return entity
            except:
                if 'to_dict' in dir(entity):
                    return entity.to_dict()
                else:
                    return str(entity)

        res = OrderedDict([(key, fullfill_entity(key, dictionate_entity(self.__dict__[key])))
                           for key in (self.json_serialize_items_list if not len(items) else items)])
        return res

    def __init__(self):
        pass

    def add(self):
        with DBConnection() as session:
            session.db.add(self)
            session.db.commit()
            return self.eachid

        return None

    @classmethod
    def delete(cls, eachid):
        with DBConnection() as session:
            res = session.db.query(cls).filter_by(eachid=eachid).all()

            if len(res):
                [session.db.delete(_) for _ in res]
                session.db.commit()
            else:
                raise FileNotFoundError('%s was not found' % cls.__name__)

    @classmethod
    def get(cls):
        with DBConnection() as session:
            return session.db.query(cls)

    @classmethod
    def process_media(cls, session, media_type, _owner_id, eachid, _id, _):
        if EntityBase.MediaCls:
            _name = ''
            _desc = ''

            if media_type == 'equipment':
                _name = _['name']
                _desc = _['desc']
                _ = _['media']

            if type(_) is str:
                resolver = MediaResolverFactory.produce(media_type, base64.b64decode(_))
                resolver.Resolve()
                _ = EntityBase.MediaCls(_owner_id, media_type, resolver.url, name=_name, desc=_desc).add()

            if type(_) is int:
                EntityBase.MediaPropCls(eachid, _id, _).add(session=session, no_commit=True)
            else:
                raise FileNotFoundError("Media has not been created")
