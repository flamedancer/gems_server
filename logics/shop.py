# -*- coding: utf-8 -*-
""" 各种兑换商店
"""

import datetime
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
    ubase = request.user
    umodified = request.user.user_modified
    shop_config = umodified._shop_config
    purchased = umodified.temp.get('shop', {})
    # 判断是否要首充标记
    if ubase.last_charge_time: 
        for info in shop_config['diamond'].values():
            info.pop('exfirstcharge_award', None) 
    # 每日限购 限购次数为最大购买次数减去已购买次数
    for shop_type in purchased.get('daily_limit', {}):
        for index in purchased[shop_type]['daily_limit']:
            conf = shop_config[shop_type][index]
            limit_cnt = conf.get('daily_limit_cnt')
            if limit_cnt:
                new_limit_cnt = limit_cnt - purchased[shop_type][index]
                conf['daily_limit_cnt'] = new_limit_cnt
    # 永久限购 限购次数为最大购买次数减去已购买次数
    for shop_type in purchased.get('forever_limit', {}):
        for index in purchased[shop_type]['forever_limit']:
            conf = shop_config[shop_type][index]
            limit_cnt = conf.get('forever_limit_cnt')
            if limit_cnt:
                new_limit_cnt = limit_cnt - purchased[shop_type][index]
                conf['forver_limit_cnt'] = new_limit_cnt
    # 出售时间限制 
    for category in ['package', 'item']:
        pop_index = []
        for index, info in shop_config[category].items():
            if 'start_sale_time' in info and 'end_sale_time' in info:
                now_str = str(datetime.datetime.now())[:-7]
                if not info['start_sale_time'] <= now_str <= info['end_sale_time']:
                    pop_index.append(index)
        for index in pop_index: 
            shop_config[category].pop(index)
            
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
    limit_type = ''
    for limit in ['daily_limit_cnt', 'forever_limit_cnt']:
        if limit in conf:
            limit_type = limit 
    if limit_type:
        limit_cnt = conf.get(limit_type)
        purchased = umodified.temp.get('shop', {}).get(limit_type[:-4], {})
        if limit_cnt <= purchased.get(shop_type, {}).get(index, 0):
            return {}
        else:
            umodified.temp.setdefault('shop', {})
            umodified.temp['shop'].setdefault(limit_type[:-4], {})
            umodified.temp['shop'][limit_type[:-4]].setdefault(shop_type, {})
            umodified.temp['shop'][limit_type[:-4]][shop_type].setdefault(index, 0)
            umodified.temp['shop'][limit_type[:-4]][shop_type][index] += 1
    return {}
    
    
