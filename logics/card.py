#-*- coding: utf-8 -*-
""" 卡牌逻辑
"""

from bottle import request
from common import tools
from common.exceptions import *


def api_switch_team_index(team_index):
    """ api/card/switch_team
    切换编队
    
    Args:
        team_index(int): 新的当前编队序号
    """
    umodified = request.user.user_modified
    ucards = request.user.user_cards
    index = ucards.set_cur_team_index(team_index)
    umodified.set_modify_info('cur_team_index', index)
    return {}

def api_set_team(team_index, new_team):
    """ api/card/set_team
    切换编队
    
    Args:
        team_index(int): 要修改的编队序号
        new_team(list): 新的编队
    """
    umodified = request.user.user_modified
    ucards = request.user.user_cards
    teams = ucards.set_team(team_index, new_team)
    umodified.set_modify_info('teams', teams)
    return {}


def api_upgrade(card_id, lv_num):
    """ api/card/upgrade
    升级卡片

    Args:
        card_id(str): 要升级的卡片id
        lv_num(int): 要升级的等级
    """
    umodified = request.user.user_modified
    ucards = request.user.user_cards
    new_card_info = ucards.add_card_lv(card_id, lv_num)
    umodified.set_modify_info('cards', {card_id: new_card_info})
    return {}
    

def api_dismiss(dismiss_type, card_id=''):
    """ api/card/dismiss
    1) 有三种分解方式    
    2)  分解所得英魂值只与卡牌的品质有关。
         i   普通：5
         ii  精良：10
         iii 稀有：25
         iv  史诗：50
         v   传说：100
    Args:
        dismiss_type(str): 分解方式
            "dismiss_one" : 分解一张此卡
            "keep_one"    : 只保留一张此卡，其他分解
            "all_keep_one": 所有卡牌只保留一张,其余全分解,card_id 缺省
        card_id(str): 卡片id
    Returns:
        get_heroSoul: 分解后产生的英魂

    """
    print "dismiss_cards", card_id, dismiss_type 
    ubase = request.user
    ucards = ubase.user_cards
    get_heroSoul = 20
    if dismiss_type == 'dismiss_one': 
        tools.del_user_things(ubase, card_id, 1, 'dismiss_card')
    elif dismiss_type == 'keep_one':
        now_num = ucards.cards.get(card_id, {}).get('num', 0)
        del_num = now_num - 1
        tools.del_user_things(ucards, card_id, del_num, 'dismiss_card')
    elif dismiss_type == 'all_keep_one':
        for cid, cinfo in ucards.cards.items():
            cnum = cinfo['num']
            if cnum <= 1:
                continue
            del_num = cnum - 1
            tools.del_user_things(ucards, cid, del_num, 'dismiss_card')
    tools.add_user_things(ubase, 'heroSoul', get_heroSoul, 'dismiss_card')
    
    return {'get_heroSoul': 20}



def api_summon(card_id):
    """ api/card/summon
    4)  卡牌的召唤费用由以下要素决定：
         i   卡牌品质
         ii  卡牌等级
         iii 卡牌好感度
    Args:
        card_id: 卡牌id

    """
    print "summon_cards", card_id
    ubase = request.user
    new_info = tools.add_user_things(ubase, card_id, 1, 'summon_card')
    # 召唤后数量应该为 1
    if new_info['num'] != 1:
        raise LogicError("The num of this card sould be 0") 
    return {}


def api_off_new(card_id):
    """ api/card/off_new
    首次查看新的卡片后，将new的标记去除
    Args:
        card_id: 卡牌id
    """
    umodified = request.user.user_modified
    ucards = request.user.user_cards
    if card_id not in ucards.cards:
        raise LogicError("Not exist card") 
    if 'is_new' in ucards.cards[card_id]:
        ucards.cards[card_id]['is_new'] = False
    umodified.set_modify_info('cards', {card_id: ucards.cards[card_id]})
    return {}
    
