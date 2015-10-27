# -*- coding:utf-8 -*-
""" 城市逻辑
"""

from bottle import request
from common import tools
from common.exceptions import *


def calcu_ex_natures(ucities, city_id):
    city_lv = ucities.cities[city_id]['lv']
    # 3,5,7,9,10级分别获得0,1,2,3,4index前加成
    get_ex_index = city_lc // 2
    lvup_nature_conf = ucities._city_config['lvup_nature']
    ex_natures_list = [0] * 6
    for natures, ex in lvup_nature_conf[:get_ex_index]):
        for nature in natures:
            ex_natures_list[nature] += ex
    uproperty = ucities.user_property
    umodified = ucities.user_modified
    for nature_type, ex in enumertate(ex_nature_list):
        nature_name = 'ex_nature_' + str(nature_type)
        setattr(uproperty, nature_name, ex)
        umodified.set_modify_info(nature_name, ex)
    uproperty.put()
    umodified.put()
        
        
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
    calcu_ex_nature(ucities, city_id)
    return {}
    

def api_open_city(city_id):
    """ api/city/open_city
    解锁城市

    Args:
        city_id(str): 要解锁的城市id
    """
    umodified = request.user.user_modified
    ucities = request.user.user_cities
    need_coin_conf = ucities._common_config["open_city_cost_coin"]
    has_opened_num = ucities.get_opened_city_num()
    need_coin = need_coin_conf[has_opened_num]
    tools.del_user_things(ucities, 'coin', need_coin, 'open_city')
    new_info = ucities.open_city(city_id)
    umodified.set_modify_info('cities', new_info)
    return {}
     
    
