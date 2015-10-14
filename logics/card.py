#-*- coding: utf-8 -*-
""" 卡牌逻辑
"""

from bottle import request
from common import tools
from common.exceptions import *


def api_switch_team_index(team_index):
    """ api/card/switch_team_index
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
    ucards = request.user.user_cards
    ucards.set_cur_team_index(team_index)
    if ucards.cur_team == new_team:
        return {} 
    umodified = request.user.user_modified
    team = ucards.set_team(team_index, new_team)
    umodified.set_modify_info('cities', {team_index: {'team': team}})
    umodified.set_modify_info('cur_team_index', team_index)
    return {}


def api_upgrade(card_id, lv_num):
    """ api/card/upgrade
    升级卡片

    Args:
        card_id(str): 要升级的卡片id
        lv_num(int): 要升级的等级
    """
    ucards = request.user.user_cards
    consume_conf = ucards._cardup_config['lvup_consume_heroSoul']
    max_card_lv = ucards._common_config.get('max_card_lv', 15)
    card_quality = str(ucards._card_config[card_id]["quality"])
    now_lv = ucards.get_card_lv(card_id)
    if now_lv + lv_num >= max_card_lv:
        raise LogicError("The card got the top lv")
    need_heroSoul = 0
    # 计算需消耗英魂
    for add_lv_cnt in range(lv_num): 
        need_heroSoul += consume_conf[card_quality][now_lv]
        now_lv += 1
    tools.del_user_things(ucards, 'heroSoul', need_heroSoul, 'card_upgrade')
    new_card_info = ucards.add_card_lv(card_id, lv_num)
    umodified = request.user.user_modified
    umodified.set_modify_info('cards', {card_id: new_card_info})
    return {}


def api_add_favor(card_id):
    """ api/card/add_favor
    卡片进阶(增加好感度)

    Args:
        card_id(str): 要进阶的卡片id
    """
    ucards = request.user.user_cards
    new_card_info = ucards.add_card_favor(card_id)
    umodified = request.user.user_modified
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
    get_heroSoul = 0
    product_conf = ubase._cardup_config['dismiss_product_heroSoul']
    card_config = ubase._card_config
    if dismiss_type == 'dismiss_one': 
        tools.del_user_things(ubase, card_id, 1, 'dismiss_card')
        card_quality = str(card_config[card_id]['quality'])
        get_heroSoul += product_conf[card_quality]
        adjust_team(ucards, card_id)
    elif dismiss_type == 'keep_one':
        now_num = ucards.cards.get(card_id, {}).get('num', 0)
        del_num = now_num - 1
        tools.del_user_things(ucards, card_id, del_num, 'dismiss_card')
        card_quality = str(card_config[card_id]['quality'])
        get_heroSoul += del_num * product_conf[card_quality]
        adjust_team(ucards, card_id)
    elif dismiss_type == 'all_keep_one':
        for cid, cinfo in ucards.cards.items():
            cnum = cinfo['num']
            if cnum <= 1:
                continue
            del_num = cnum - 1
            tools.del_user_things(ucards, cid, del_num, 'dismiss_card')
            card_quality = str(card_config[cid]['quality'])
            get_heroSoul += del_num * product_conf[card_quality]
            adjust_team(ucards, cid)
    tools.add_user_things(ubase, 'heroSoul', get_heroSoul, 'dismiss_card')
    return {'get_heroSoul': get_heroSoul}


def adjust_team(ucards, card_id):
    """ 调整编队
    当原编队中卡片数量不足时，从头到尾剔除不再满足数量条件的卡片
    """
    cur_num = ucards.cards[card_id]['num']
    if cur_num >= 4:
        return
    ucities = ucards.user_cities
    umodified = ucards.user_modified
    for city_id in ucities.cities:
        team = ucities.cities[city_id]['team']
        inteam_num = team.count(card_id)
        if inteam_num <= cur_num:
            continue
        should_drop_num = inteam_num - cur_num
        new_team = []
        for cid in team:
            if cid != card_id or should_drop_num <= 0:
                new_team.append(cid)
            else:
                new_team.append('')
                should_drop_num -= 1
        ucities.cities[city_id]['team'] = new_team
        umodified.set_modify_info('cities', {city_id: {'team': new_team}})
    ucities.put()
        
            
def api_summon(card_id):
    """ api/card/summon
    召唤所需金币=品质系数+200*(当前等级-1)+800*当前好感度
    Args:
        card_id: 卡牌id

    """
    print "summon_cards", card_id
    ucards = request.user.user_cards
    summon_coe =ucards._cardup_config['summon_coe'] 
    card_quality = str(ucards._card_config[card_id]["quality"])
    card_lv = ucards.get_card_lv(card_id)
    now_favor = int(ucards.cards[card_id]['favor'])
    need_coin = summon_coe[card_quality] + 200 * (card_lv - 1) + 800 * now_favor
    tools.del_user_things(ucards, 'coin', need_coin, 'summon_card')
    new_info = tools.add_user_things(ucards, card_id, 1, 'summon_card')
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
    
