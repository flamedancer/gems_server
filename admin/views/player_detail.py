#-*- coding:utf-8 -*-

import settings
from bottle import request, route, redirect
from bottle import jinja2_view as view
from models.user_base import UserBase 
from admin.decorators import validate
from common import tools
from logics import card as card_logic
from logics import login

card_words = {
    # 品质
    'quality': [u'普通', u'精良', u'稀有', u'史诗', u'传说'],
    # 神话
    'myth': [u'北欧', u'希腊', u'中国', u'日本', u'印度', u'埃及', u'犹太', u'凯尔特', u'阿兹特克', u'阿拉伯', u'美索不达米亚', u'所罗门魔神', u'其他', u'无'],
    # 阵营
    'camp': [u'纳达拉城', u'科洛西尔', u'塔塔洛斯', u'尤克特',u'拉希尔', u'祖尔阿兹兰', u'圣光天庭', u'云雾峰', u'萨拉曼德', u'潘德曼尼南', u'冥界', u'格拉德海姆', u'赫利波利斯', u'特兰西瓦尼亚', u'无'],
    # 种族
    'race': [u'恶魔', u'野兽', u'妖鬼', u'天使', u'精灵', u'龙', u'亡灵', u'无'],
    # 元素
    'type': [u'蓝', u'红', u'绿', u'褐', u'黄', u'紫'],
    # 攻击模式
    'attack_type': [u'爪击', u'锐器攻击', u'撞击', u'魔法攻击'],
}


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
        detail['detail_category'] = 'cards'
        detail.update(ubase.user_cards.to_dict())
        print detail
        detail['card_config'] = ubase._card_config
        detail['card_words'] = card_words
        detail['sorted_cards'] = login.dirtolist(detail['card_config'])
    return detail

def can_modify():
    if request.employee.is_super() or settings.DEBUG:
        return True 
    return False


@route('/admin/modify_player/add_cards/<player_uid>', method="POST")
@validate
def add_cards(player_uid):
    if not can_modify():
        raise
    ubase = UserBase.get(player_uid)
    new_cards = request.forms.getlist('new_cards')
    card_num = int(request.forms.get('card_num', 1))
    for card_id in new_cards:
        tools.add_user_things(ubase, card_id, card_num, 'admin')
    redirect("/admin/player_detail?uid=%s&category=cards" % player_uid)
    

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
        new_name = request.forms.get('newname')
        update_name = tools.update_user_info(ubase, 'name', new_name, 'admin')
        return update_name

    elif modify_type.endswith('_card_lv'):
        ucards = ubase.user_cards
        card_id = modify_type.rsplit('_lv', 1)[0]
        new_lv = int(request.forms.get(modify_type)) 
        ucards.cards[card_id]['lv'] = new_lv
        ucards.put()

    elif modify_type.endswith('_card_favor'):
        ucards = ubase.user_cards
        card_id = modify_type.rsplit('_favor', 1)[0]
        new_lv = int(request.forms.get(modify_type)) 
        ucards.cards[card_id]['favor'] = new_lv
        ucards.put()

    elif modify_type.endswith('_card_num'):
        ucards = ubase.user_cards
        card_id = modify_type.rsplit('_num', 1)[0]
        new_lv = int(request.forms.get(modify_type)) 
        ucards.cards[card_id]['num'] = new_lv
        ucards.put()
    
    elif modify_type.startswith('dismiss_'):
        ucards = ubase.user_cards
        card_id = modify_type.split('dismiss_', 1)[1]
        dismiss_type = request.forms.get(modify_type)
        request.user = ubase
        card_logic.api_dismiss(dismiss_type, card_id)

    elif modify_type.startswith('summon_'):
        ucards = ubase.user_cards
        card_id = modify_type.split('summon_', 1)[1]
        num = int(request.forms.get(modify_type)) 
        request.user = ubase
        card_logic.api_summon(card_id)
        
        
    else:
        thing = modify_type[1:]
        num = int(request.forms.get('add' + thing))
        return tools.add_user_things(ubase, thing, num, 'addby_admin')
    

        

