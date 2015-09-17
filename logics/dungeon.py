# -*- coding: utf-8 -*-
""" 战斗
"""

from bottle import request
from logics import card

def check_can_start():
    pass


def api_start(dungeon_type, city_id, team_index='', new_team=None):
    """ api/dungeon/start
    进战场
    Args:
        dungeon_type(str): 战斗类型 "conquer"征服模式 "challenge"挑战模式 
        city_id(str): 要打哪个城，城市id
        team_index(str): 选取的城市编队id
        new_team(list->str): 新的战斗卡片队伍

    Returns:
        enemy_team(list): 敌将编队
        enemy_lv(list->int): 各敌将等级
        enemy_favor(int): 敌将全元素好感度
    """
    check_can_start()
    card.api_set_team(team_index, new_team)

    
    result = {'enemy_team': ['1_card', '2_card', '3_card', '4_card'],
            'enemy_lv': [1, 2, 3, 4, 5],
            'enemy_favor': 3,
    }
    return result


def api_end(dungeon_type, city_id):
    """ api/dungeopn/end
    结束战斗
    Args:
        dungeon_type(str): 战斗类型 "conquer"征服模式 "challenge"挑战模式 
        city_id(str): 要打哪个城，城市id

    """
    pass

    
    
