# -*- coding: utf-8 -*-
""" 抽卡
"""
import random
from bottle import request
from common.utils import get_key_by_weight_dict
from common.tools import *


def gacha(gacha_type):
    """ 两种gacha_type
        金币抽: coin_gacha
        钻石抽: diamond_gacha
    """
    user = request.user
    get_cards = []

    gacha_conf = user._gacha_config[gacha_type]
    color_rate_dict = {key: value['weight'] for key,value in gacha_conf.items()}
    get_green = False
    for cnt in range(0, 3):
        # 前两张没拿到绿卡，第三张必出
        if cnt == 2 and not get_green:
            color = '1'
        else:
            color = get_key_by_weight_dict(color_rate_dict) 
        if color == '1':
            get_green = True
        cid_rate_dict = {key: value['weight'] for key, value in gacha_conf[color].items() if key != 'weight'}
        card_key = get_key_by_weight_dict(cid_rate_dict) 
        get_card = gacha_conf[color][card_key]['id']
        get_cards.append(get_card)
        color_rate_dict[color] -= 1
        
        
    for card_id in get_cards:
        add_user_things(user, card_id, 1, gacha_type)

    return get_cards


def api_coin_gacha():
    """ api/gacha/coin_gacha
    用金币抽卡,获得三张卡牌,必有一张绿卡

    Returns:
       get_cards(list): 获得的卡牌序列 
    """
    return {'get_cards': gacha('coin_gacha')}


def api_diamond_gacha():
    """ api/gacha/diamond_gacha
    用钻石抽卡

    Returns:
       get_cards(list): 获得的卡牌序列 
    """
    return {'get_cards': gacha('diamond_gacha')}
