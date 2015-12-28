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
    
   
def api_show_shop():
    """ api/shop/show_shop
    返回商城商品信息
    """
    umodified = request.user.user_modified
    shop_config = umodified._shop_config
    purchased = umodified.temp.get('shop', {})
    # 限购次数为最大购买次数减去已购买次数
    for shop_type in purchased:
        for index in purchased[shop_type]:
            conf = shop_config[shop_type][index]
            limit_cnt = conf['limit_cnt']
            new_limit_cnt = limit_cnt - purchased[shop_type][index]
            conf['limit_cnt'] = new_limit_cnt
    return shop_config 
    
    
def api_shopping(shop_type, index):
    """ api/shop/shopping
    商城购买，消耗真实货币 
    Args:
        shop_type(str): 商品类型 【dimaond, item, coin, heroSoul】
        index(str): 商品序号
    """
    umodified = request.user.user_modified
    shop_config = umodified._shop_config
    if shop_type not in shop_config or index not in shop_config[shop_type]:
        return {}
    # 判断购买次数是否超过
    conf = shop_config[shop_type][index]
    limit_cnt = conf['limit_cnt']
    purchased = umodified.temp.get('shop', {})
    if limit_cnt <= purchased.get(shop_type, {}).get(index, 0):
        return {}
    return {}
    
    
