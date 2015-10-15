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
    common_config = user._common_config
    if gacha_type == 'coin_gacha':
        need_coin = common_config['gacha_coin']
        del_user_things(user, 'coin', need_coin, gacha_type)
    elif gacha_type == 'diamond_gacha':
        need_diamond = common_config['gacha_diamond']
        del_user_things(user, 'diamond', need_diamond, gacha_type)
    
    get_cards = []

    gacha_conf = user._gacha_config[gacha_type]
    color_rate_dict = {key: value['weight'] for key,value in gacha_conf.items()}
    guarant_color = 2 if gacha_type == 'diamond_gacha' else 1 
    get_guarant = False
    for cnt in range(0, 3):
        # 前两张没拿到保底颜色或以上卡，第三张必出保底颜色或以上
        if cnt == 2 and not get_guarant:
            for key_color in range(0, guarant_color):
                color_rate_dict.pop(key_color, None)
            color = get_key_by_weight_dict(color_rate_dict) 
        else:
            color = get_key_by_weight_dict(color_rate_dict) 
        if int(color) >= guarant_color:
            get_guarant = True
        cid_rate_dict = {key: value['weight'] for key, value in gacha_conf[color].items() if key != 'weight'}
        card_key = get_key_by_weight_dict(cid_rate_dict) 
        get_card = gacha_conf[color][card_key]['id']
        get_cards.append(get_card)
        color_rate_dict[color] -= 1
        
        
    for card_id in get_cards:
        add_user_things(user, card_id, 1, gacha_type)

    # 打乱顺序
    random.shuffle(get_cards)
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
