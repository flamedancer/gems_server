# -*- coding: utf-8 -*-
""" 城战逻辑
"""
import time
from bottle import request
from common.exceptions import *
from common import tools 
from common.utils import get_key_by_weight_dict


def api_info():
    """ api/invade/info
    城战界面基本信息
    Returns:
        cup(int): 奖杯数
        cup_rank(int): 城战段位
        shield_time(int): 保护结束时间
        watch_team(list->str): 防守队伍
        has_new_history(bool): 是否有新的防守日志
        refresh_coin(int): 寻找对手需要金币 
        opponent(dict): 对手信息，没对手时为空
            uid(str): 对手uid
            name(str): 对手名字
            lv(int): 多少等级
            expire_time(int): 此对手过期时间
            capitail_city(str): 对手主城id
            win_award(dict): 胜利获得奖励
            lose_award(dict)；失败获得奖励

        例如:
        {
            'cup': 3,
            'cup_rank': 15,
            'shield_time': 1445333584,
            'watch_team': ['1_card', '2_card', '3_card', '4_card'],
            'refresh_coin': 50,
            'opponent': {
                'name': 'xxx',
                'lv':  45,
                'expire_time': 1453434344,
                'captial_city': '0',
                'win_award': {
                    'coin': 40,
                    'cup': 1,
                },
                'lose_award': {
                    'cup': -1,
                },
            },
        }

    """
    return {
            'cup': 3,
            'cup_rank': 15,
            'shield_time': int(time.time()) + 3650,
            'watch_team': ['1_card', '2_card', '3_card', '4_card'],
            'refresh_coin': 50,
            'opponent': {
                'name': 'xxx',
                'lv':  45,
                'expire_time': int(time.time()) + 120,
                'captial_city': '0',
                'win_award': {
                    'coin': 40,
                    'cup': 1,
                },
                'lose_award': {
                    'cup': -1,
                },
            },
        }
 

def api_history():
    """ api/invade/history
    Retures:
        history(list->dict): 防守日志
            'status': 状态  0被侵略  1反击胜利 
            'name': 侵略人名
            'lv': 侵略人等级 
            'captial_city': 侵略人主城id
            'cup': 侵略人奖杯数
            'team': 侵略人编队
            'time': 时间
            'lose_coin': 损失金币数(status0 时)
            'win_invade_jeton': 获得城战代币数(status1时)
    """
    return { 'history': [
                {
                    'status': 0,
                    'uid': 'xxx',
                    'name': 'xxxxx', 
                    'lv': 40,
                    'captial_city': '0',
                    'cup': 10,
                    'time': int(time.time()) - 3600,
                    'lose_coin': 40,
                },
                

        ]
    }



def api_store():
    """ api/invade/store
    返回商店配置
    """
    return {
        '1': {
            'invade_jeton': 10,
            'award': {
                'coin': 20,
            }
        }
    }

    
    


def api_find_opponent():
    """ api/invade/find_opponent
    寻找对手
    Retures:
        同api_info
    """
    return {
            'cup': 3,
            'cup_rank': 15,
            'shield_time': int(time.time()) + 3650,
            'watch_team': ['1_card', '2_card', '3_card', '4_card'],
            'refresh_coin': 50,
            'opponent': {
                'name': 'xxx',
                'lv':  45,
                'expire_time': int(time.time()) + 120,
                'captial_city': '0',
                'win_award': {
                    'coin': 40,
                    'cup': 1,
                },
                'lose_award': {
                    'cup': -1,
                },
            },
        }

def api_start_invade(team_index='', new_team=None):
    """ api/invade/start_invade
    开打
    Args:
        new_team(list): 战斗编队
    Returns:
        enemy(dict):
            uid: 敌人uid
            name: 敌人名字
            lv: 敌人等级
            nature_*: 敌人各元素掌握度
            team: 敌人卡片队伍
            card_lv(list->int): 各卡片等级
            card_favor(list->int): 各卡片好感度
        
    """
    return { 'enemy': {
                'lv': 10,
                'nature_0': 5,
                'nature_1': 5,
                'nature_2': 5,
                'nature_3': 5,
                'nature_4': 5,
                'nature_5': 5,
                'team': ['1_card', '2_card', '3_card', '4_card'],
                'card_lv': [2, 4, 6, 8],
                'card_favor':[0, 1, 0, 1],
            }
    }
    


def api_end_invade(win=True):
    """ api/invade/end_invade
    战斗胜利
    Argv:
        win(bool): 是否胜利
    """ 
    return {'award': {
                'cup': 1,
                'coin': 10,
        }
    }


def api_start_defense():
    """ api/invade/end_defense
    开始反击战斗
    """ 
    pass


def api_end_defense():
    """ api/invade/end_defense
    结束反击战斗
    """ 
    pass


def api_set_watch_team(new_team):
    """ api/invade/set_watch_team
    更改防守编队队形
    Args:
        new_team(list): 新的卡片编队 
    """
    return {}

def api_buy():
    """ api/invade/buy
    购买城战商品
    """
    uarena = request.user.user_arena
    award = uarena._arenaaward_config[str(uarena.win)]
    return {'awards': award}


