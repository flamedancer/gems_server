# -*- coding:utf-8 -*-
""" 城市逻辑
"""

from bottle import request
from common import tools
from common.exceptions import *


def api_set_capital(city_id):
    """ api/city/set_capital
    设置主城

    Args:
        city_id(str): 要设置的主城id
    """
    ucities = request.user.user_cities
    ucities.set_capital(city_id)
    umodified = ucities.user_modified
    umodified.set_modify_info('capital_city', city_id)
    return {}
    

def api_open_city(city_id):
    """ api/city/open_city
    解锁城市

    Args:
        city_id(str): 要解锁的城市id
    """
    umodified = request.user.user_modified
    ucities = request.user.user_cities
    if ucities.has_open_city(city_id):
        return {}
    # 开城等级限制
    need_lv = ucities._city_config[city_id]["need_ulv"]
    if ucities.user_property.lv < need_lv:
        raise LogicError("Should reach the open lv")
    need_coin_conf = ucities._common_config["open_city_cost_coin"]
    has_opened_num = ucities.get_opened_city_num()
    need_coin = need_coin_conf[has_opened_num]
    tools.del_user_things(ucities, 'coin', need_coin, 'open_city')
    new_info = ucities.open_city(city_id)
    umodified.set_modify_info('cities', new_info)
    return {}


def api_get_city_award():
    """ api/city/get_city_award 
    领取城市进贡
    """
    ucities = request.user.user_cities
    award = ucities.city_award
    tools.add_user_awards(ucities, award, 'city_award')
    language = ubase._language_config['award_msg']['city']
    now = datetime.datetime.now()
    return {'type': 'city',
            'award': award,
            'content1': language['content1'],
            'content2': language['content2'] % (60 - now.minute),
            "title": language['title'],
            
    }
         
    
