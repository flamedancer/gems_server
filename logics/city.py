# -*- coding:utf-8 -*-
""" 城市逻辑
"""

from bottle import request
from common import tools
from common.exceptions import *


def calcu_ex_natures(ucities, city_id):
    city_lv = ucities.cities[city_id]['lv']
    # 3,5,7,9,10级分别获得0,1,2,3,4index前加成
    get_ex_index = city_lv // 2
    lvup_nature_conf = ucities._city_config[city_id]['lvup_nature']
    ex_natures_list = [0] * 6
    for natures, ex in lvup_nature_conf[:get_ex_index]:
        for nature in natures:
            ex_natures_list[nature] += ex
    uproperty = ucities.user_property
    umodified = ucities.user_modified
    for nature_type, ex in enumerate(ex_natures_list):
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
    calcu_ex_natures(ucities, city_id)
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
    # 城市每张满级卡加一级
    ucards = ucities.user_cards
    max_card_lv = ucards._common_config['max_card_lv']
    card_config = ucards._card_config
    for card_id, card_info in ucards.cards.items():
        if card_info['lv'] == max_card_lv and\
           city_id == str(card_config[card_id]['camp']):
            ucities.up_city_lv(city_id)
    return {}
     
    
