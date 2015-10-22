# -*- coding: utf-8 -*-
""" 城战逻辑
"""
import time
from bottle import request
from logics import card
from common.exceptions import *
from common import tools 
from common.invade_user import InvadeUser
from models.user_invade import UserInvade


def api_info():
    """ api/invade/info
    城战界面基本信息
    Returns:
        cup(int): 奖杯数
        cup_rank(int): 城战段位
        invade_jeton: 城战代币
        shield_time(int): 保护结束时间
        watch_team(list->str): 防守队伍
        has_new_history(bool): 是否有新的防守日志
        refresh_coin(int): 寻找对手需要金币 
        opponent(dict): 对手信息，没对手时为空
            uid(str): 对手uid
            name(str): 对手名字
            lv(int): 多少等级
            expire_time(int): 此对手过期时间
            capital_city(str): 对手主城id
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
                'capital_city': '0',
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
    uInvade = requesr.user.user_invade
    coin_conf = uInvade._common_config['invade_refresh_coin']
    refresh_coin = coin_conf[min(uInvade.refresh_cnt, len(coin_conf) - 1)]
    # 若对手已过期 ，清空对手信息
    if uInvade.opponent['expire_time'] > time.time():
        uInvade.clear_opponent()
    return {
        'cup': uInvade.cup,
        'cup_rank': uInvade.cup_rank,
        'invade_jeton': uInvade.invade_jeton,
        'shield_time': uInvade.shield_time,
        'watch_team': uInvade.watch_team,
        'has_new_history': uInvade.has_new_history,
        'refresh_coin': refresh_coin,
        'opponent': uInvade.opponent,
    }
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
            'capital_city': 侵略人主城id
            'cup': 侵略人奖杯数
            'time': 时间
            'lose_coin': 损失金币数(status0时)
            'win_invade_jeton': 获得城战代币数(status1时)
    """
    
    return {'history': request.user.user_invade.history}
    return { 'history': [
                {
                    'status': 0,
                    'uid': 'xxx',
                    'name': 'xxxxx', 
                    'lv': 40,
                    'capital_city': '0',
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
    coin_conf = uInvade._common_config['invade_refresh_coin']
    refresh_coin = coin_conf[min(uInvade.refresh_cnt, len(coin_conf) - 1)]
    uInvade = request.user.user_invade
    tools.del_user_things(uInvade, 'coin', refresh_coin, 'invade')
    opponent_info = InvadeUser.get().get_fight_user(except_uids=[uInvade.uid])
    # 失败只损失一个奖杯
    opponent_info['lose_award'] = {
        'cup': -1,
    }
    userlv_config = uInvade._userlv_config
    win_get_coin = userlv_config[str(opponent['lv'])].get('reward_coin', 10) if opponent_info['uid'] else 0
    opponent_info['win_award'] = {
        'cup': 1,
        'coin': win_get_coin,
    }
    uInvade.set_opponent(opponent_info)
    return opponent_info
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
        team_index(str): 选取的那个城编队去打
    Returns:
        enemy(dict):
            nature_*: 敌人各元素掌握度
            team: 敌人卡片队伍
            card_lv(list->int): 各卡片等级
            card_favor(list->int): 各卡片好感度
        
    """
    if team_index != '' and new_team is not None:
        if set(new_team) == set(['']):
            raise ParmasError('Can\'t set empty team !')
        card.api_set_team(team_index, new_team) 
    uInvade = request.user.user_invade
    opponent_info = uInvade.opponent
    opponent_uid = opponent_info['uid']
    # 记录战前信息
    umodified = uInvade.user_modified
    umodified.temp['dungeon'] = {
        'type': 'invade',
        'time': int(time.time()),
    }
    umodified.put()
    # 如果是虚拟玩家，造一个数据
    if not opponent_uid:
        opponent_info = {
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
    else:
        opponent_team_info = UserInvade.get(opponent_uid).watch_team_info()
    # 每次打别人， 自己的保护时间取消
    uInvade.reset_shield_time()
    return {'enemy': opponent_team_info}
    


def api_end_invade(win=True):
    """ api/invade/end_invade
    战斗胜利
    Argvs:
        win(bool): 是否胜利
    Returns:
        award(dict): 结束奖励
    
    """ 
    user = request.user
    umodified = ubase.user_modified
    if 'dungeon' not in umodified.temp:
        raise LogicError('Should start fight first')
    start_info = umodified.temp['dungeon']
    if start_info.get('type') != 'invade':
        raise LogicError('End the wrong fight')
    umodified.temp.pop('dungeon')
    umodified.put()
    now = int(time.time())
    if now - start_info['time'] <= 1:
        raise LogicError("rush a dungeon to quick") 

    uInvade = user.user_invade
    uProperty = uInvade.user_property
    opponent_info = uInvade.opponent
    opponent_uid = opponent_info['uid']
    invade_log = {
        'status': 0,
        'name': user.name,
        'lv': uProperty.lv, 
        'cup': uInvade.cup,
        'time': int(time.time()),
    }
    invade_log['team_info'] = uInvade.now_team_info()
    # 胜利获得奖杯和对手金钱;失败扣奖杯,且对手加代币
    if win:
        award = opponent['win_award']
        award['exp'] = 30
        invade_log['lose_coin'] = award.get('coin', 0)
    else:
        award = opponent['lose_award']
        award['exp'] = 10
        invade_log['win_invade_jeton'] = abs(award.get('invade_jeton', 0))

    # 改变对手数据！ 加代币 或 减钱
    if opponent_uid:
        opponentInvade = UserInvade.get(opponent_uid)
        # 日志中主城设为被打者主城
        invade_log['capital_city'] = opponentInvade.user_city.capital_city
        if win:
            opponent_coin = opponentInvade.user_property.coin 
            award['coin'] = max(invade_log['lose_coin'], opponent_coin) 
            tools.del_user_things(opponentInvade, 'coin', award['coin'], 'beinvaded')
            # 打赢了 要告诉对手
            opponentInvade.add_history(invade_log)
        else:
            opponentInvade.add_invade_jeton(1)
    else:
        award['coin'] = 0
        
    # 给自己加奖励
    if 'cup' in award:
        add_cup = uInvade.add_cup(award['cup'])
        award['cup'] = add_cup
    tools.add_user_awards(user, award, 'invade')
    return award


def api_start_defense(history_index, team_index='', new_team=None):
    """ api/invade/start_defense
    开始反击战斗
    Args:
        history_index(int): 所反击历史记录的index
        new_team(list): 战斗编队
        team_index(str): 选取的那个城编队去打
    Returns:
        enemy(dict):
            nature_*: 敌人各元素掌握度
            team: 敌人卡片队伍
            card_lv(list->int): 各卡片等级
            card_favor(list->int): 各卡片好感度
    """ 
    if team_index != '' and new_team is not None:
        if set(new_team) == set(['']):
            raise ParmasError('Can\'t set empty team !')
        card.api_set_team(team_index, new_team) 
    uInvade = request.user.user_invade
    history = uInvade.history
    if not 0 <= history_index <= len(history) - 1:
        raise ParamsError('Wrong history index') 
    defe_history = history[history_index]
    if defe_history['status'] != 0:
        raise LogicError('Had been defensed')


    # 记录战前信息
    umodified = uInvade.user_modified
    umodified.temp['dungeon'] = {
        'type': 'invade_defense',
        'history': defe_history,
        'time': int(time.time()),
    }
    umodified.put()
    # 重置 连续寻找对手次数 清空对手已找到对手记录 清除此次日志
    uInvade.reset_refresh_cnt()
    uInvade.clear_opponent()
    uInvade.clear_history(index=history_index)
    return {'enemy': defe_history['team_info']}


def api_end_defense(win=True):
    """ api/invade/end_defense
    结束反击战斗
    
    """ 
    award = {'exp': 3}
    if not win:
        return {'award': award}
    user = request.user
    umodified = ubase.user_modified
    if 'dungeon' not in umodified.temp:
        raise LogicError('Should start fight first')
    start_info = umodified.temp['dungeon']
    if start_info.get('type') != 'invade_defense':
        raise LogicError('End the wrong fight')
    defe_history = start_info['history']
    umodified.temp.pop('dungeon')
    umodified.put()
    now = int(time.time())
    if now - start_info['time'] <= 1:
        raise LogicError("rush a dungeon to quick") 

    uInvade = user.user_invade
    award = {
        'exp': 9,
        'invade_jeton': 1,
    } 
    # 加代币
    uInvade.add_invade_jeton(1)
    tools.add_user_awards(uInvade, award, 'invade_denfense')
    # 加日志
    defe_history['status'] = 1
    defe_history['win_invade_jeton'] = 1
    defe_history['time'] = int(time.time())
    uInvade.add_history(defe_history)
    
    return award

    
def api_set_watch_team(new_team):
    """ api/invade/set_watch_team
    更改防守编队队形
    Args:
        new_team(list): 新的卡片编队 
    """
    uInvade = request.user.user_invade
    uInvade.set_watch_team(new_team)
    return {}

def api_buy(good_id):
    """ api/invade/buy
    购买城战商品
    Argvs:
        good_id(str): 商品号
    """
    return {'awards': }


