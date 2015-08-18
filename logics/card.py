#-*- coding: utf-8 -*-
""" 卡牌逻辑
"""

from bottle import request
from common import tools

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
    tools.add_user_things(ubase, card_id, 1, 'summon_card')
