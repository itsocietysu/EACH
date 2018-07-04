from collections import OrderedDict
import time
import datetime

from sqlalchemy import Column, String, Integer, Date, Sequence
from sqlalchemy.ext.declarative import declarative_base

from each.Entities.EntityBase import EntityBase
from each.Entities.EntityUser import EntityUser
from each.Entities.EntityCourt import EntityCourt
from each.Entities.EntityLocation import EntityLocation
from each.Entities.EntityProp import EntityProp
from each.Entities.EntityPost import EntityPost

from each.Prop.PropBool import PropBool
from each.Prop.PropLocation import PropLocation
from each.Prop.PropReal import PropReal
from each.Prop.PropPost import PropPost

from each.db import DBConnection

def serach_objects(params):
    def mock_bool(_id, _val, _type):
        return PropBool.get()\
            .filter(PropBool.propid == _id)\
            .filter(PropBool.value == _val)\
            .all()

    def mock_name(_id, _val, _type):
        #lambda _id, _val, _type: meta_object_map[_type].get()
        #.filer(meta_object_map[_type].name.startswith(_val)).all()
        return meta_object_map[_type].get()\
        .filter(meta_object_map[_type].name.startswith(_val)).all()

    meta_prop_name = EntityProp.map_name_id()
    meta_prop_name.update({'name': -1})
    meta_prop_name.update({'location_area': meta_prop_name['location']})

    meta_object_map = {
        'user': EntityUser,
        'court': EntityCourt,
        'location': EntityLocation,
        'post': EntityPost
    }

    meta_filter_map = {
        'location': lambda _id, _val, _type: PropLocation.get()
            .filter(PropLocation.propid == _id)
            .filter(PropLocation.value == _val).all(),

        'location_area': lambda _id, _val, _type: PropLocation.get_object_in_area(_id, _val[0:2], _val[2]),

        'private': mock_bool,
        'isopen': mock_bool,
        'isfree': mock_bool,
        'isonair': mock_bool,

        'price': lambda _id, _val, _type: PropReal.get()
            .filter(PropReal.propid == _id)
            .filter(PropReal.value.between(_val[0], _val[1])).all(),

        'name': mock_name,
    }

    _type = params["object"]
    _prop = params["prop"]

    res = set([])
    for k, v in _prop.items():
        new_set = set([_.eachid
                       if _type in ['court', 'user', 'post'] or k == 'name'
                       else _.value
                       for _ in meta_filter_map[k](meta_prop_name[k], v, _type)])
        if not len(res):
            res = new_set
        else:
            res = res.intersection(new_set)

    return meta_object_map[_type], list(res)
