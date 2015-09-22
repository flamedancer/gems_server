# -*- coding: utf-8 -*-
""" 抽卡
"""
#from common.utils import get_items_by_weight_dict
from common.tools import *



def api_coin_gacha():
    """ api/gacha/coin_gacha
    用金币抽卡,获得三张卡牌,必有一张绿卡

    Returns:
       get_cards(list): 获得的卡牌序列 
    """
    user = request.user
    get_cards = ['1_card', '2_card', '3_card']
    for card_id in get_cards:
        add_user_things(user, card_id, 1, 'coin_gacha')
    return {'get_cards': get_cards}


def api_diamond_gacha():
    """ api/gacha/diamond_gacha
    用钻石抽卡

    Returns:
       get_cards(list): 获得的卡牌序列 
    """
    return {'get_cards': ['1_card', '2_card', '3_card']}
