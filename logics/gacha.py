# -*- coding: utf-8 -*-
""" 抽卡
"""


def api_coin_gacha():
    """ api/gacha/coin_gacha
    用金币抽卡

    Returns:
       get_cards(list): 获得的卡牌序列 
    """
    return {'get_cards': ['1_card', '2_card', '3_card']}


def api_diamond_gacha():
    """ api/gacha/diamond_gacha
    用钻石抽卡

    Returns:
       get_cards(list): 获得的卡牌序列 
    """
    return {'get_cards': ['1_card', '2_card', '3_card']}
