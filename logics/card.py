#-*- coding: utf-8 -*-
""" 卡牌逻辑
"""

from bottle import request
from common import tools


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
    ucards = request.user.user_cards
    ucards.add_card_lv(card_id, lv_num)
    return {}
    

def api_dismiss(card_id, num):
    """ api/card/dismiss
    3)  分解所得英魂值只与卡牌的品质有关。
         i   普通：5
         ii  精良：10
         iii 稀有：25
         iv  史诗：50
         v   传说：100
    Args:
        card_id: 卡片id
        num:     要分解的数量
    Returns:
        get_heroSoul: 分解后产生的英魂

    """
    print "dismiss_cards", card_id, num
    ubase = request.user
    tools.del_user_things(ubase, card_id, num, 'dismiss_card')
    get_heroSoul = 20
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
    tools.add_user_things(ubase, card_id, 1, 'summon_card')
