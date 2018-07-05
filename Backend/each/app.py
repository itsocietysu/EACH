import concurrent.futures as ftr
import json
import logging
import mimetypes
import os
import posixpath
import re
import time
from collections import OrderedDict

import falcon
from falcon_multipart.middleware import MultipartMiddleware

from each import utils
from each.db import DBConnection
from each.serve_swagger import SpecServer

from each.MediaResolver.MediaResolverFactory import MediaResolverFactory

def guess_response_type(path):
    if not mimetypes.inited:
        mimetypes.init()  # try to read system mime.types

    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream',  # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
    })

    base, ext = posixpath.splitext(path)
    if ext in extensions_map:
        return extensions_map[ext]
    ext = ext.lower()
    if ext in extensions_map:
        return extensions_map[ext]
    else:
        return extensions_map['']

def date_time_string(timestamp=None):
    weekdayname = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    monthname = [None,
                 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    if timestamp is None:
        timestamp = time.time()
    year, month, day, hh, mm, ss, wd, y, z = time.gmtime(timestamp)
    s = "%s, %02d %3s %4d %02d:%02d:%02d GMT" % (
            weekdayname[wd],
            day, monthname[month], year,
            hh, mm, ss)
    return s

def httpDefault(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    path = req.path
    src_path = path
    path = path.replace(baseURL, '.')

    if os.path.isdir(path):
        for index in "index.html", "index.htm", "test-search.html":
            index = os.path.join(path + '/', index)
            if os.path.exists(index):
                path = index
                break
        else:
            return None

    if path.endswith('swagger.json'):
        path = path.replace('swagger.json', 'swagger_temp.json')

    ctype = guess_response_type(path)

    try:
        with open(path, 'rb') as f:
            resp.status = falcon.HTTP_200

            fs = os.fstat(f.fileno())
            length = fs[6]

            buffer = f.read()
            if path.endswith('index.html'):
                str = buffer.decode()
                str = str.replace('127.0.0.1:4201', server_host)
                buffer = str.encode()
                length = len(buffer)

    except IOError:
        resp.status = falcon.HTTP_404
        return

    resp.set_header("Content-type", ctype)
    resp.set_header("Content-Length", length)
    resp.set_header("Last-Modified", date_time_string(fs.st_mtime))
    resp.set_header("Access-Control-Allow-Origin", "*")
    resp.set_header("Path", path)
    resp.body = buffer

def getVersion(**request_handler_args):
    resp = request_handler_args['resp']
    resp.status = falcon.HTTP_501
    with open("VERSION") as f:
        resp.body = obj_to_json({"version": f.read()})

def initDatabase(**request_handler_args):
    resp = request_handler_args['resp']

    #with DBConnection() as db:
    #    db.init()

    resp.status = falcon.HTTP_501

def cleanupDatabase(**request_handler_args):
    resp = request_handler_args['resp']
    #with DBConnection() as db:
    #    db.Cleanup()

    resp.status = falcon.HTTP_501

def getAllCourts(**request_handler_args):
    resp = request_handler_args['resp']

    objects = EntityCourt.get().all()

    resp.body = obj_to_json([o.to_dict() for o in objects])
    resp.status = falcon.HTTP_200

def getCourtById(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam('courtId', **request_handler_args)
    objects = EntityCourt.get().filter_by(eachid=id).all()

    e_mail = req.context['email']
    my_id = EntityUser.get_id_from_email(e_mail)

    wide_info = EntityCourt.get_wide_object(id)

    res = []
    for _ in objects:
        obj_dict = _.to_dict()

        wide_info['is_mine'] = my_id == obj_dict['ownerid']
        wide_info['followed'] = EntityFollow.get().filter_by(eachid=my_id, followingid=id).count() > 0
        wide_info['followers_amount'] = EntityFollow.get().filter_by(followingid=id).count()
        my_like = [_ for _ in wide_info['like'] if int(_['userid']) == my_id]
        wide_info['liked'] = len(my_like) > 0
        wide_info['my_rate'] = my_like[0]['weight'] if wide_info['liked'] else 0.0
        wide_info['rate_count'] = len(wide_info['like'])
        wide_info['rate_avg'] = sum([int(_['weight']) for _ in wide_info['like']]) / float(wide_info['rate_count']) \
            if wide_info['rate_count'] > 0 \
            else 0.0

        obj_dict.update(wide_info)
        res.append(obj_dict)

    resp.body = obj_to_json(res)
    resp.status = falcon.HTTP_200


def easyCreateCourt(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    e_mail = req.context['email']
    ownerid = EntityUser.get_id_from_email(e_mail)

    media = []
    for _ in sorted(req.params.keys()):
        if _.startswith('Photo'):
            data = req.get_param(_)

            resolver = MediaResolverFactory.produce('image', data.file.read())
            resolver.Resolve()

            media.append(EntityMedia(ownerid, 'image', resolver.url, name='', desc='').add())

    equipment = []
    for _ in sorted(req.params.keys()):
        if _.startswith('EqPhoto'):
            name = req.get_param(_.replace('Photo', 'Name'))
            desc = req.get_param(_.replace('Photo', 'Desc'))
            data = req.get_param(_)

            resolver = MediaResolverFactory.produce('equipment', data.file.read())
            resolver.Resolve()

            equipment.append({
                'name': name,
                'desc': desc,
                'media': EntityMedia(ownerid, 'equipment', resolver.url, name=name, desc=desc).add()
            })

    if 'LocationName' in req.params.keys() and 'Latitude' in req.params.keys() and 'Longitude' in req.params.keys():
        location = EntityLocation(req.get_param('LocationName'),
                                  req.get_param('Latitude'),
                                  req.get_param('Longitude')).add()

    params = {}

    params['ownerid'] = ownerid
    params['name'] = req.get_param('Name')
    params['desc'] = req.get_param('Desc')
    params['prop'] = {}
    params['prop']['media'] = media
    params['prop']['equipment'] = equipment
    params['prop']['location'] = location

    id = EntityCourt.add_from_json(params)

    if id:
        objects = EntityCourt.get().filter_by(eachid=id).all()

        resp.body = obj_to_json([o.to_dict() for o in objects])
        resp.status = falcon.HTTP_200


def createCourt(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']


    e_mail = req.context['email']
    ownerid = EntityUser.get_id_from_email(e_mail)

    params = json.loads(req.stream.read().decode('utf-8'))
    params['ownerid'] = ownerid

    id = EntityCourt.add_from_json(params)

    if id:
        objects = EntityCourt.get().filter_by(eachid=id).all()

        resp.body = obj_to_json([o.to_dict() for o in objects])
        resp.status = falcon.HTTP_200


def updateCourt(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    resp.status = falcon.HTTP_501


def deleteCourt(**request_handler_args):
    resp = request_handler_args['resp']

    id = getIntPathParam('courtId', **request_handler_args)

    if id is not None:
        try:
            EntityCourt.delete(id)
        except FileNotFoundError:
            resp.status = falcon.HTTP_404
            return

        try:
            EntityCourt.delete_wide_object(id)
        except FileNotFoundError:
            resp.status = falcon.HTTP_405
            return

        object = EntityCourt.get().filter_by(eachid=id).all()
        if not len(object):
            resp.status = falcon.HTTP_200
            return

    resp.status = falcon.HTTP_400


def createUser(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    try:
        params = json.loads(req.stream.read().decode('utf-8'))
        id = EntityUser.add_from_json(params)

        if id:
            objects = EntityUser.get().filter_by(eachid=id).all()

            resp.body = obj_to_json([o.to_dict() for o in objects])
            resp.status = falcon.HTTP_200
            return
    except ValueError:
        resp.status = falcon.HTTP_405
        return

    resp.status = falcon.HTTP_501


def updateUser(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    try:
        params = json.loads(req.stream.read().decode('utf-8'))
        id = EntityUser.update_from_json(params)

        if id:
            objects = EntityUser.get().filter_by(eachid=id).all()

            resp.body = obj_to_json([o.to_dict() for o in objects])
            resp.status = falcon.HTTP_200
            return
    except ValueError:
        resp.status = falcon.HTTP_405
        return

    resp.status = falcon.HTTP_501


def getAllUsers(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    objects = EntityUser.get().all()

    resp.body = obj_to_json([o.to_dict() for o in objects])
    resp.status = falcon.HTTP_200


def getUserById(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam("userId", **request_handler_args)
    objects = EntityUser.get().filter_by(eachid=id).all()

    e_mail = req.context['email']
    my_id = EntityUser.get_id_from_email(e_mail)

    wide_info = EntityUser.get_wide_object(id, ['private', 'avatar', 'post'])

    wide_info['post'].sort(key=lambda x: x['eachid'], reverse=True)

    wide_info['is_me'] = my_id == id
    wide_info['followed'] = EntityFollow.get().filter_by(eachid=my_id, followingid=id).count() > 0
    wide_info['following_amount'] = EntityFollow.get().filter_by(eachid=id).count()
    wide_info['followers_amount'] = EntityFollow.get().filter_by(followingid=id).count()

    res = []
    for _ in objects:
        obj_dict = _.to_dict(['eachid', 'name'])
        obj_dict.update(wide_info)
        res.append(obj_dict)

    resp.body = obj_to_json(res)
    resp.status = falcon.HTTP_200


def getMyUser(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    e_mail = req.context['email']
    id = EntityUser.get_id_from_email(e_mail)

    objects = EntityUser.get().filter_by(eachid=id).all()

    #TODO: LIMIT the posts output counts with a paging
    wide_info = EntityUser.get_wide_object(id, ['private', 'avatar', 'post'])

    wide_info['post'].sort(key=lambda x: x['eachid'], reverse=True)
    followings = EntityFollow.get().filter_by(eachid=id).all()
    wide_info['is_me'] = True
    wide_info['followed'] = False
    wide_info['following_amount'] = len(followings)
    wide_info['followers_amount'] = EntityFollow.get().filter_by(followingid=id).count()

    res = []
    for _ in objects:
        obj_dict = _.to_dict(['eachid', 'name'])
        obj_dict.update(wide_info)
        res.append(obj_dict)

    resp.body = obj_to_json(res)
    resp.status = falcon.HTTP_200


def deleteUser(**request_handler_args):
    resp = request_handler_args['resp']
    req = request_handler_args['req']

    #TODO: VERIFICATION IF ADMIN DELETE ANY
    e_mail = req.context['email']
    id_from_req = getIntPathParam("userId", **request_handler_args)
    id = EntityUser.get_id_from_email(e_mail)

    if id is not None:
        if id != id_from_req:
            resp.status = falcon.HTTP_400
            return

        try:
            EntityUser.delete(id)
        except FileNotFoundError:
            resp.status = falcon.HTTP_404
            return

        try:
            EntityUser.delete_wide_object(id)
        except FileNotFoundError:
            resp.status = falcon.HTTP_405
            return

        object = EntityUser.get().filter_by(eachid=id).all()
        if not len(object):
            resp.status = falcon.HTTP_200
            return

    resp.status = falcon.HTTP_400


def getPostAffectedUsers(post):
    res = [post['userid']]

    for _ in post['comment']:
        res.append(_['userid'])

    for _ in post['like']:
        res.append(_['userid'])

    return res


def getUserFollowingsPosts(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    e_mail = req.context['email']
    id = EntityUser.get_id_from_email(e_mail)

    followingIDs = [_.followingid for _ in EntityFollow.get()
        .filter_by(eachid=id)
        .filter(EntityFollow.permit >= EntityUser.PERMIT_ACCESSED).all()]

    posts = EntityPost.get().filter(EntityPost.userid.in_(followingIDs))\
        .order_by(EntityPost.eachid.desc())\
        .limit(1000).all()

    post_section = []
    for _ in posts:
        obj_dict = _.to_dict(['eachid', 'userid', 'description'])
        obj_dict.update(EntityPost.get_wide_object(_.eachid))
        post_section.append(obj_dict)

    user_list = []
    for _ in post_section:
        user_list.extend(getPostAffectedUsers(_))

    users_affected_ids = list(set(user_list))
    users = EntityUser.get().filter(EntityUser.eachid.in_(users_affected_ids))

    user_section = {}
    for _ in users:
        obj_dict = _.to_dict(['eachid', 'name'])
        obj_dict.update(EntityUser.get_wide_object(_.eachid, ['private', 'avatar']))
        user_section.update({_.eachid: obj_dict})

    resp.body = obj_to_json({'post': post_section, 'user': user_section})
    resp.status = falcon.HTTP_200


def userAddFollowing(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    e_mail = req.context['email']
    id = EntityUser.get_id_from_email(e_mail)

    id_to_follow = getIntPathParam("followingId", **request_handler_args)
    EntityFollow(id, id_to_follow, EntityUser.PERMIT_NONE
                                    if EntityUser.is_private(id_to_follow)
                                    else EntityUser.PERMIT_ACCESSED, True).add()

    resp.status = falcon.HTTP_200


def userDelFollowing(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    e_mail = req.context['email']
    id = EntityUser.get_id_from_email(e_mail)

    id_to_follow = getIntPathParam("followingId", **request_handler_args)
    EntityFollow.smart_delete(id, id_to_follow)

    resp.status = falcon.HTTP_200

def getUserFollowingsList(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam("userId", **request_handler_args)

    resp.status = falcon.HTTP_200
    resp.body   = obj_to_json([_.to_dict() for _ in EntityFollow.get()
                      .filter_by(eachid=id)
                      .filter(EntityFollow.permit >= EntityUser.PERMIT_ACCESSED).all()])


def getUserFollowersList(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam("userId", **request_handler_args)

    resp.status = falcon.HTTP_200
    resp.body   = obj_to_json([_.to_dict() for _ in EntityFollow.get()
                            .filter_by(followingid=id).all()])


def getUserFollowersRequestList(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam("userId", **request_handler_args)

    resp.status = falcon.HTTP_200
    resp.body   = obj_to_json([_.to_dict() for _ in EntityFollow.get()
                        .filter_by(followingid=id)
                        .filter(EntityFollow.permit == EntityUser.PERMIT_NONE).all()])


def userResolveFollowerRequest(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    e_mail = req.context['email']
    id = EntityUser.get_id_from_email(e_mail)

    id_to_resolve = getIntPathParam('followerId', **request_handler_args)
    accept = req.params['accept']

    if not accept:
        EntityFollow.smart_delete(id_to_resolve, id)
    else:
        EntityFollow.update(id_to_resolve, id, EntityUser.PERMIT_ACCESSED)

    resp.status = falcon.HTTP_200


def createMedia(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    e_mail = req.context['email']
    ownerid = EntityUser.get_id_from_email(e_mail)
    media_type = req.params['type']
    name = req.params['name'] if 'name' in req.params else ''
    desc = req.params['desc'] if 'desc' in req.params else ''

    results = []
    for key in (_ for _ in req._params.keys() if _.startswith('file')):
        data = req.get_param(key)
        try:
            resolver = MediaResolverFactory.produce(media_type, data.file.read())
            resolver.Resolve()

            #TODO:NO NULL HERE AS OWNER
            id = EntityMedia(ownerid, media_type, resolver.url, name=name, desc=desc).add()
            if id:
                results.append(id)
        except Exception as e:
            resp.status = falcon.HTTP_400
            resp.body = obj_to_json("Media uploading error\nException::\n" + str(e))
            return

    resp.body = obj_to_json(results)
    resp.status = falcon.HTTP_200


def getAllOwnerMedias(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam('ownerId', **request_handler_args)

    if id is not None:
        objects = EntityMedia.get().filter_by(ownerid=id).all()
        resp.body = obj_to_json([o.to_dict() for o in objects])
        resp.status = falcon.HTTP_200
        return

    resp.status = falcon.HTTP_500


def getMedia(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam('mediaId', **request_handler_args)

    if id is not None:
        objects = EntityMedia.get().filter_by(eachid=id).all()

        resp.body = obj_to_json([o.to_dict() for o in objects])
        resp.status = falcon.HTTP_200
        return

    resp.status = falcon.HTTP_500

def deleteMedia(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam('mediaId', **request_handler_args)

    if id:
        try:
            EntityMedia.delete(id)
        except FileNotFoundError:
            resp.status = falcon.HTTP_404
            return

        object = EntityMedia.get().filter_by(eachid=id).all()
        if not len(object):
            resp.status = falcon.HTTP_200
            return

    resp.status = falcon.HTTP_500


def createLocation(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    try:
        params = json.loads(req.stream.read().decode('utf-8'))
        name = params.get('name')
        latitude = params.get('latitude')
        longitude = params.get('longitude')
    except ValueError:
        resp.status = falcon.HTTP_405
        return

    if not name:
        resp.status = falcon.HTTP_405
        return

    id = EntityLocation(name, latitude, longitude).add()

    if id:
        objects = EntityLocation.get().filter_by(eachid=id).all()

        resp.body = obj_to_json([o.to_dict() for o in objects])
        resp.status = falcon.HTTP_200
        return

    resp.status = falcon.HTTP_500


def getLocationById(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam('locId', **request_handler_args)

    if id is not None:
        objects = EntityLocation.get().filter_by(eachid=id).all()

        resp.body = obj_to_json([o.to_dict() for o in objects])
        resp.status = falcon.HTTP_200
        return

    resp.status = falcon.HTTP_500


def deleteLocation(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam('locId', **request_handler_args)

    if id is not None:
        try:
            EntityLocation.delete(id)
        except FileNotFoundError:
            resp.status = falcon.HTTP_404
            return

        object = EntityLocation.get().filter_by(eachid=id).all()
        if not len(object):
            resp.status = falcon.HTTP_200
            return

    resp.status = falcon.HTTP_400


def getAllLocations(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    objects = EntityLocation.get().all()#PropLike.get_object_property(0, 0)#

    resp.body = obj_to_json([o.to_dict() for o in objects])
    resp.status = falcon.HTTP_200


def getPostById(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam("postId", **request_handler_args)
    objects = EntityPost.get().filter_by(eachid=id).all()

    wide_info = EntityPost.get_wide_object(id)

    post_section = []
    for _ in objects:
        obj_dict = _.to_dict()
        obj_dict.update(wide_info)
        post_section.append(obj_dict)

    user_list = []
    for _ in post_section:
        user_list.extend(getPostAffectedUsers(_))

    users_affected_ids = list(set(user_list))
    users = EntityUser.get().filter(EntityUser.eachid.in_(users_affected_ids))

    user_section = {}
    for _ in users:
        obj_dict = _.to_dict(['eachid', 'name'])
        obj_dict.update(EntityUser.get_wide_object(_.eachid, ['private', 'avatar']))
        user_section.update({_.eachid: obj_dict})

    resp.body = obj_to_json({'post': post_section, 'user': user_section})
    resp.status = falcon.HTTP_200


def getAllPosts(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    objects = EntityPost.get().all()

    resp.body = obj_to_json([o.to_dict() for o in objects])
    resp.status = falcon.HTTP_200

def createPost(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    userId = EntityUser.get_id_from_email(req.context['email'])

    if userId is None:
        resp.status = falcon.HTTP_405
        return

    params = json.loads(req.stream.read().decode('utf-8'))
    id = EntityPost.add_from_json(params, userId)

    if id:
        objects = EntityPost.get().filter_by(eachid=id).all()

        resp.body = obj_to_json([o.to_dict() for o in objects])
        resp.status = falcon.HTTP_200
        return

    resp.status = falcon.HTTP_500


def updatePost(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    try:
        params = json.loads(req.stream.read().decode('utf-8'))
        id = EntityPost.update_from_json(params)

        if id:
            objects = EntityPost.get().filter_by(eachid=id).all()

            resp.body = obj_to_json([o.to_dict() for o in objects])
            resp.status = falcon.HTTP_200
            return
    except ValueError:
        resp.status = falcon.HTTP_405
        return

    resp.status = falcon.HTTP_501


def deletePost(**request_handler_args):
    resp = request_handler_args['resp']

    id = getIntPathParam('postId', **request_handler_args)

    if id is not None:
        try:
            EntityPost.delete(id)
        except FileNotFoundError:
            resp.status = falcon.HTTP_404
            return

        try:
            EntityPost.delete_wide_object(id)
        except FileNotFoundError:
            resp.status = falcon.HTTP_405
            return

        object = EntityPost.get().filter_by(eachid=id).all()
        if not len(object):
            resp.status = falcon.HTTP_200
            return

    resp.status = falcon.HTTP_400


def search(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    params = json.loads(req.stream.read().decode('utf-8'))

    _cls, ids = serach_objects(params)

    result = []
    for _ in _cls.get().filter(_cls.eachid.in_(list(ids))).all():
        obj_dict = _.to_dict()
        if 'get_wide_object' in _cls.__dict__:
            obj_dict.update(_cls.get_wide_object(_.eachid, ['private', 'avatar'] if _cls.__name__ == 'EntityUser' else []))

        result.append(obj_dict)

    resp.body = obj_to_json(result)
    resp.status = falcon.HTTP_200


def getLikeById(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam("likeId", **request_handler_args)
    objects = EntityLike.get().filter_by(eachid=id).all()

    res = []
    for _ in objects:
        obj_dict = _.to_dict()
        res.append(obj_dict)

    resp.body = obj_to_json(res)
    resp.status = falcon.HTTP_200


def getAllLikes(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    objects = EntityLike.get().all()

    resp.body = obj_to_json([o.to_dict() for o in objects])
    resp.status = falcon.HTTP_200


def updateLike(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    try:
        params = json.loads(req.stream.read().decode('utf-8'))
        id = EntityLike.update_from_json(params)

        if id:
            objects = EntityLike.get().filter_by(eachid=id).all()

            resp.body = obj_to_json([o.to_dict() for o in objects])
            resp.status = falcon.HTTP_200
            return
    except ValueError:
        resp.status = falcon.HTTP_405
        return

    resp.status = falcon.HTTP_501


def deleteLike(**request_handler_args):
    resp = request_handler_args['resp']

    id = getIntPathParam('likeId', **request_handler_args)

    if id is not None:
        try:
            EntityLike.delete(id)
            PropLike.delete_value(id, raise_exception=False)
        except FileNotFoundError:
            resp.status = falcon.HTTP_404
            return

        object = EntityLike.get().filter_by(eachid=id).all()
        if not len(object):
            resp.status = falcon.HTTP_200
            return

    resp.status = falcon.HTTP_400


def createLike(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    params = json.loads(req.stream.read().decode('utf-8'))
    userId = EntityUser.get_id_from_email(req.context['email'])

    if userId is None:
        resp.status = falcon.HTTP_405
        return

    id = EntityLike.add_from_json(params, userId)

    if id:
        objects = EntityLike.get().filter_by(eachid=id).all()

        resp.body = obj_to_json([o.to_dict() for o in objects])
        resp.status = falcon.HTTP_200
        return

    resp.status = falcon.HTTP_422


def getCommentById(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    id = getIntPathParam("commentId", **request_handler_args)
    objects = EntityComment.get().filter_by(eachid=id).all()

    res = []
    for _ in objects:
        obj_dict = _.to_dict()
        res.append(obj_dict)

    resp.body = obj_to_json(res)
    resp.status = falcon.HTTP_200


def getAllComments(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    objects = EntityComment.get().all()

    resp.body = obj_to_json([o.to_dict() for o in objects])
    resp.status = falcon.HTTP_200


def updateComment(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    try:
        params = json.loads(req.stream.read().decode('utf-8'))
        id = EntityComment.update_from_json(params)

        if id:
            objects = EntityComment.get().filter_by(eachid=id).all()

            resp.body = obj_to_json([o.to_dict() for o in objects])
            resp.status = falcon.HTTP_200
            return
    except ValueError:
        resp.status = falcon.HTTP_405
        return

    resp.status = falcon.HTTP_501


def deleteComment(**request_handler_args):
    resp = request_handler_args['resp']

    id = getIntPathParam('commentId', **request_handler_args)

    if id is not None:
        try:
            EntityComment.delete(id)
            PropComment.delete_value(id, raise_exception=False)
        except FileNotFoundError:
            resp.status = falcon.HTTP_404
            return

        object = EntityComment.get().filter_by(eachid=id).all()
        if not len(object):
            resp.status = falcon.HTTP_200
            return

    resp.status = falcon.HTTP_400


def createComment(**request_handler_args):
    req = request_handler_args['req']
    resp = request_handler_args['resp']

    params = json.loads(req.stream.read().decode('utf-8'))
    userId = EntityUser.get_id_from_email(req.context['email'])

    if userId is None:
        resp.status = falcon.HTTP_405
        return

    id = EntityComment.add_from_json(params, userId)

    if id:
        objects = EntityComment.get().filter_by(eachid=id).all()

        resp.body = obj_to_json([o.to_dict() for o in objects])
        resp.status = falcon.HTTP_200
        return

    resp.status = falcon.HTTP_500


operation_handlers = {
    'initDatabase':    [initDatabase],
    'cleanupDatabase': [cleanupDatabase],
    'getVersion':      [getVersion],
    'httpDefault':     [httpDefault],

    #Court methods
    'getAllCourts':           [getAllCourts],
    'getCourtById':           [getCourtById],
    'createCourt':            [createCourt],
    'updateCourt':            [updateCourt],
    'deleteCourt':            [deleteCourt],
    'easyCreateCourt':        [easyCreateCourt],

    #User methods
    'createUser':             [createUser],
    'updateUser':             [updateUser],
    'getAllUsers':            [getAllUsers],
    'getUser':                [getUserById],
    'getMyUser':              [getMyUser],
    'deleteUser':             [deleteUser],
    'getUserFollowingsList':        [getUserFollowingsList],
    'getUserFollowingsPosts':       [getUserFollowingsPosts],
    'userAddFollowing':             [userAddFollowing],
    'userDelFollowing':             [userDelFollowing],
    'getUserFollowersList':         [getUserFollowersList],
    'getUserFollowersRequestList':  [getUserFollowersRequestList],
    'userResolveFollowerRequest':   [userResolveFollowerRequest],

    #Media methods
    'createMedia':            [createMedia],
    'getAllOwnerMedias':      [getAllOwnerMedias],
    'getMedia':               [getMedia],
    'deleteMedia':            [deleteMedia],

    #Location methods
    'createLocation':         [createLocation],
    'getLocationById':        [getLocationById],
    'deleteLocation':         [deleteLocation],
    'getAllLocations':        [getAllLocations],

    #Post methods
    'getPostById':          [getPostById],
    'getAllPosts':          [getAllPosts],
    'createPost':           [createPost],
    'updatePost':           [updatePost],
    'deletePost':           [deletePost],

    #Search methods
    'search':               [search],

    # Like methods
    'getLikeById':          [getLikeById],
    'getAllLikes':          [getAllLikes],
    'updateLike':           [updateLike],
    'deleteLike':           [deleteLike],
    'createLike':           [createLike],

    # Comment methods
    'getCommentById':       [getCommentById],
    'getAllComments':       [getAllComments],
    'updateComment':        [updateComment],
    'deleteComment':        [deleteComment],
    'createComment':        [createComment]
}

class CORS(object):
    def process_response(self, req, resp, resource):
        origin = req.get_header('Origin')
        if origin:
            resp.set_header('Access-Control-Allow-Origin', origin)
            resp.set_header('Access-Control-Max-Age', '100')
            resp.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS, PUT, DELETE')
            resp.set_header('Access-Control-Allow-Credentials', 'true')

            acrh = req.get_header('Access-Control-Request-Headers')
            if acrh:
                resp.set_header('Access-Control-Allow-Headers', acrh)

            # if req.method == 'OPTIONS':
            #    resp.set_header('Access-Control-Max-Age', '100')
            #    resp.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS, PUT, DELETE')
            #    acrh = req.get_header('Access-Control-Request-Headers')
            #    if acrh:
            #        resp.set_header('Access-Control-Allow-Headers', acrh)


class Auth(object):
    def process_request(self, req, resp):
        #TODO: SWITCH ON
        #req.context['email'] = 'serbudnik@gmail.com'
        #return
        # skip authentication for version, UI and Swagger
        if re.match('(/each/version|'
                     '/each/settings/urls|'
                     '/each/images|'
                     '/each/ui|'
                     '/each/swagger\.json|'
                     '/each/swagger-temp\.json|'
                     '/each/swagger-ui).*', req.relative_uri):
            return

        if req.method == 'OPTIONS':
            return # pre-flight requests don't require authentication

        token = None
        try:
            if req.auth:
                token = req.auth.split(" ")[1].strip()
            else:
                token = req.params.get('access_token')
        except:
            raise falcon.HTTPUnauthorized(description='Token was not provided in schema [berear <Token>]',
                                      challenges=['Bearer realm=http://GOOOOGLE'])

        error = 'Authorization required.'
        if token:
            error, res, email = auth.Validate(token, auth.PROVIDER.GOOGLE)
            if not error:
                req.context['email'] = email

                if not EntityUser.get_id_from_email(email) and not re.match('(/each/user).*', req.relative_uri):
                    raise falcon.HTTPUnavailableForLegalReasons(description=
                                                                "Requestor [%s] not existed as user yet" % email)

                return # passed access token is valid

        raise falcon.HTTPUnauthorized(description=error,
                                      challenges=['Bearer realm=http://GOOOOGLE'])


logging.getLogger().setLevel(logging.DEBUG)
args = utils.RegisterLaunchArguments()

cfgPath = args.cfgpath
profile = args.profile
# configure
with open(cfgPath) as f:
    cfg = utils.GetAuthProfile(json.load(f), profile, args)
    DBConnection.configure(**cfg['each_db'])
    if 'oidc' in cfg:
        cfg_oidc = cfg['oidc']

general_executor = ftr.ThreadPoolExecutor(max_workers=20)

wsgi_app = api = falcon.API(middleware=[CORS(), Auth(), MultipartMiddleware()])

server = SpecServer(operation_handlers=operation_handlers)

if 'server_host' in cfg:
    with open('swagger.json') as f:
        swagger_json = json.loads(f.read(), object_pairs_hook=OrderedDict)

    server_host = cfg['server_host']
    swagger_json['host'] = server_host

    baseURL = '/each'
    if 'basePath' in swagger_json:
        baseURL = swagger_json['basePath']

    json_string = json.dumps(swagger_json)

    with open('swagger_temp.json', 'wt') as f:
        f.write(json_string)

with open('swagger_temp.json') as f:
    server.load_spec_swagger(f.read())

api.add_sink(server, r'/')
