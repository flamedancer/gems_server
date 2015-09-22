# -*- coding: utf-8 -*-
""" 战斗
"""

import time
from bottle import request
from logics import card
from common import tools
from common.exceptions import *

def check_can_start():
    pass


def api_start(dungeon_type, city_id, team_index='', new_team=None):
    """ api/dungeon/start
    进战场
    1.进战场先扣体力 
    2.进战场会先给1/3经验值
    Args:
        dungeon_type(str): 战斗类型 "conquer"征服模式 "challenge"挑战模式 
        city_id(str): 要打哪个城，城市id
        team_index(str): 选取的城市编队id
        new_team(list->str): 新的战斗卡片队伍

    Returns:
        enemy_team(list): 敌将编队
        enemy_lv(list->int): 各敌将等级
        enemy_favor(int): 敌将全好感度
        enemy_nature(int): 敌将全元素掌握度
    """
    check_can_start()
    if team_index != '' and new_team is not None:
        if set(new_team) == set(['']):
            raise ParmasError('Can\'t set empty team !')
        card.api_set_team(team_index, new_team)
    ubase = request.user
    ucities = ubase.user_cities
    if dungeon_type == 'conquer':
        conquer_config = ubase._conquer_config  
        if city_id not in conquer_config:
            raise LogicError("Has no this city")
        if not ucities.can_conquer_city(city_id):
            raise LogicError("Can't conquer this city")
        cur_stage = str(ucities.cur_conquer_stage(city_id))
        stage_conf = conquer_config[city_id][cur_stage]
        need_stamina = stage_conf['stamina']
        # 扣体力
        tools.del_user_things(ubase, 'stamina', need_stamina, 'conquer')
        # 加1/3经验 
        add_exp = int((1.0 / 3) * stage_conf['award'].get('exp', 0))
        tools.add_user_things(ubase, 'exp', add_exp, 'conquer')
        enemy_favor = stage_conf['enemy_favor'] 
        enemy_nature = stage_conf['enemy_nature'] 
        enemy_team = []
        enemy_lv = []
        for enemy_cid, lv in stage_conf['enemy']:
            enemy_team.append(enemy_cid)
            enemy_lv.append(lv)

        umodified = ubase.user_modified
        umodified.temp['dungeon'] = {
            'type': dungeon_type,
            'time': int(time.time()),
            'city_id': city_id,
        }
        umodified.put()
        
        result = {
            'enemy_team': enemy_team,
            'enemy_lv': enemy_lv,
            'enemy_favor': enemy_favor,
            'enemy_nature': enemy_nature,
            'add_exp': add_exp,
        }
        return result
    return {}


def api_end(dungeon_type, city_id):
    """ api/dungeon/end
    结束战斗
    Args:
        dungeon_type(str): 战斗类型 "conquer"征服模式 "challenge"挑战模式 
        city_id(str): 要打哪个城，城市id

    Returns:
        award(dir): 奖励
            例:
             'award' :{
                "coin":170,
                "exp":10,
                "diamond":10,
                "heroSoul":70,
                "card":[
                    [
                        "10_card",
                        1
                    ]
                ]
            },

    """
    ubase = request.user
    ucities = ubase.user_cities
    umodified = ubase.user_modified 
    if 'dungeon' not in umodified.temp:
        raise LogicError
    start_info = umodified.temp['dungeon']
    if start_info['type'] != dungeon_type or \
       start_info['city_id'] != city_id:
        raise LogicError
    now = int(time.time())
    if now - start_info['time'] <= 1:
        raise LogicError("rush a dungeon to quick")
    if dungeon_type == 'conquer':
        conquer_config = ubase._conquer_config  
        cur_stage = ucities.cur_conquer_stage(city_id)
        stage_conf = conquer_config[city_id][cur_stage]
        award = stage_conf.get('award', {})
        if 'exp' in award:
            # 加2/3经验 
            add_exp = award['exp'] - int((1.0 / 3) * award['exp'])
            award['exp'] = add_exp
        if str(int(ucities.cur_conquer_stage(city_id)) + 1) not in stage_conf:
            ucities.conquer_city(city_id)
        else:
            ucities.up_conquer_stage(city_id)
        for thing, info in award.items():
            # 'card' : [['1_card', 1]...
            if thing == 'card':
                for cid, num in info:
                    tools.add_user_things(ubase, cid, num, 'conquer')
            else:
                tools.add_user_things(ubase, thing, info, 'conquer')
        return award

