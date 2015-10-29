# -*- coding: utf-8 -*-
""" 抽卡
"""
import random
from bottle import request
from common.utils import get_key_by_weight_dict
from common.tools import *


def gacha(gacha_type):
    """ 两种gacha_type
        金币抽: coin
        钻石抽: diamond
    """
    user = request.user
    common_config = user._common_config
    if gacha_type == 'coin':
        del_user_things(user, 'gachacoin_item', 1, gacha_type)
    elif gacha_type == 'diamond':
        del_user_things(user, 'gachadiamond_item', 1, gacha_type)
    
    get_cards = []

    gacha_conf = user._gacha_config[gacha_type + '_gacha']
    color_rate_dict = {key: value['weight'] for key,value in gacha_conf.items()}
    guarant_color = 2 if gacha_type == 'diamond' else 1 
    get_guarant = False
    for cnt in range(0, 3):
        # 前两张没拿到保底颜色或以上卡，第三张必出保底颜色或以上
        if cnt == 2 and not get_guarant:
            for key_color in range(0, guarant_color):
                color_rate_dict.pop(str(key_color), None)
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


def api_gacha(gacha_type):
    """ api/gacha/gacha
    抽卡,获得三张卡牌,必有一张绿卡
    Args:
        gacha_type(str): 抽卡类型: 'diamond'(钻石抽), 'coin'(金币抽) 

    Returns:
       get_cards(list): 获得的卡牌序列 
    """
    return {'get_cards': gacha(gacha_type)}


def api_buy_gacha_item(gacha_type):
    """ api/gacha/buy_gacha_item
    购买抽卡道具
    Args:
        gacha_type(str): 购买的道具类型: 'diamond'(钻石抽道具), 'coin'(金币抽道具) 
    """
    user = request.user
    common_config = user._common_config
    if gacha_type == 'coin':
        need_coin = common_config['gacha_coin']
        del_user_things(user, 'coin', need_coin, 'buy_gachacoin_item')
        add_user_things(user, 'gachacoin_item', 1, 'buy_gachacoin_item')
    elif gacha_type == 'diamond':
        need_diamond = common_config['gacha_diamond']
        del_user_things(user, 'diamond', need_diamond, 'buy_gachadiamond_item')
        add_user_things(user, 'gachadiamond_item', 1, 'buy_gachadiamond_item')
    return {}
    
