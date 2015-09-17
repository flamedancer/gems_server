# -*- coding:utf-8 -*-
""" 城市逻辑
"""

from bottle import request
from common import tools
from common.exceptions import *


def api_open_city(city_id):
    """ api/city/open_city
    解锁城市

    Args:
        city_id(str): 要解锁的城市id
    """
    umodified = request.user.user_modified
    ucities = request.user.user_cities
    need_coin_conf = ucities._common_config["open_city_cost_coin"]
    has_opened_num = len(ucities.cities)
    need_coin = need_coin_conf[has_opened_num]
    tools.del_user_things(ucities, 'coin', need_coin)  
    new_info = ucities.open_city(city_id)
    umodified.set_modify_info('cities', new_info)
    return {}
     
    
