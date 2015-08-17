#-*- coding:utf-8 -*-

import settings
from bottle import request, route
from bottle import jinja2_view as view
from models.user_base import UserBase 
from admin.decorators import validate
from common import tools


@route('/admin/player_detail/<player_uid>', method='GET')
@route('/admin/player_detail', method='GET')
@view('player_detail.html')
@validate
def player_detail(player_uid=''):
    detail = {'can_modify': can_modify()}
    player_uid = player_uid or request.query.get('uid')
    if not player_uid:
        return {}
    print "uid", player_uid
    ubase = UserBase.get(player_uid) 
    print "ubase", ubase
    if not ubase:
        return {'uid': ''}
    category = request.query.get('category')
    if not category:
        detail.update(ubase.to_dict())
        detail.update(ubase.user_property.to_dict())
    elif category == 'cards':
        detail.update(ubase.user_cards.to_dict())
        detail['detail_category'] = 'cards'
    return detail

def can_modify():
    if request.employee.is_super() or settings.DEBUG:
        return True 
    return False


@route('/admin/modify_player', method="POST")
@validate
def modify_player():
    if not can_modify():
        raise
    player_uid = request.forms.get('uid')
    ubase = UserBase.get(player_uid)
    if not ubase:
        raise
    modify_type = request.forms.get('type')
    if not modify_type:
        raise
    print "modfiy_type", modify_type
    if modify_type == 'uname':
        newname = request.forms.get('newname')
        ubase.name = newname
        ubase.put()
        return newname
    else:
        thing = modify_type[1:]
        num = int(request.forms.get('add' + thing))
        return tools.add_user_things(ubase, thing, num, 'addby_admin') 
    

        

