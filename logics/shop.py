# -*- coding: utf-8 -*-
""" 各种兑换商店
"""

from bottle import request
from common.exceptions import *
from common import tools


def api_reputation_shopping(city_id, index):
    """ api/shop/reputation_shopping
    购买某城声望商品，消耗此城代币 
    Args:
        city_id(str): 购买那个城的商品
        index(str): 商品序号
    """
    ucities = request.user.user_cities
    reputationshop_config = ucities._reputationshop_config
    if city_id not in reputationshop_config or index not in reputationshop_config[city_id]:
        return {}
    shop = reputationshop_config[city_id][index]
    need_reputation_lv = shop['need_reputation_lv']
    # 城市声望必须达到指定条件
    if need_reputation_lv > ucities.cities[city_id]['reputation_lv']:
        return {}
    # 消耗城市代币
    new_info = ucities.add_city_jeton(city_id, -shop['cost_city_jeton'])
    ucities.user_modified.set_modify_info('cities', new_info)
    # 添加奖励
    tools.add_user_awards(ucities, shop['award'], 'reputation_shopping')
    return {}
    

def api_invade_shopping(index):
    """ api/shop/invade_shopping
    购买城战商品，消耗城战代币 
    Args:
        index(str): 商品序号
    """
    uinvade = request.user.user_invade
    invadeshop_config = uinvade._invadeshop_config
    if index not in invadeshop_config:
        return {}
    shop = invadeshop_config[index]
    # 消耗城战代币
    tools.del_user_things(uinvade, 'invade_jeton', shop['cost_invade_jeton'], 'invade_shopping')
    # 添加奖励
    tools.add_user_awards(uinvade, shop['award'], 'invade_shopping')
    return {}
    
   
    
