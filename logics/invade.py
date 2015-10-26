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


def check_remain_dungeon():
    user = request.user
    umodified = user.user_modified
    if umodified.has_dungeon_info('invade'):
        api_end_invade(win=False)
    elif umodified.has_dungeon_info('invade_defense'):
        api_end_defense(win=False)
        


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
    uInvade = request.user.user_invade
    coin_conf = uInvade._common_config['invade_refresh_coin']
    refresh_coin = coin_conf[min(uInvade.refresh_cnt, len(coin_conf) - 1)]
    # 若对手已过期 ，清空对手信息
    if uInvade.opponent.get('expire_time', 0) < time.time():
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
    uInvade = request.user.user_invade
    uInvade.has_new_history = False
    uInvade.put()
    return {'history': uInvade.history}


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
    uInvade = request.user.user_invade
    common_config = uInvade._common_config
    umodified = uInvade.user_modified
    # 消耗金币
    coin_conf = common_config['invade_refresh_coin']
    refresh_coin = coin_conf[min(uInvade.refresh_cnt, len(coin_conf) - 1)]
    tools.del_user_things(uInvade, 'coin', refresh_coin, 'invade_find')
    # 自增连续寻找对手次数
    uInvade.inc_refresh_cnt()
    # 需找对手, 添加过期时间
    invade_user_instance = InvadeUser.get_instance()
    opponent_info = invade_user_instance.get_fight_user(except_uids=[uInvade.uid])
    expire_time = common_config['invade_keep_opponent_seconds'] + int(time.time())
    opponent_info['expire_time'] = expire_time
    # 此对手不能被别的玩家搜到
    if opponent_info['uid']:
        invade_user_instance.add_user(opponent_info['uid'], expire_time)
    
    # 失败只损失一个奖杯
    opponent_info['lose_award'] = {
        'cup': -1,
    }
    # 掠夺的金币和对手主城进贡有关
    userlv_config = uInvade._userlv_config
    win_get_coin = userlv_config[str(opponent_info['lv'])].get('reward_coin', 10) if opponent_info['uid'] else 0
    # 连胜两次以上获得两个杯，否则一个
    opponent_info['win_award'] = {
        'cup': 1 if uInvade.consecutive_win < 2 else 2,
        'coin': win_get_coin,
    }
    # 记录下对手信息,若有旧对手,将他的过期时间重置
    if uInvade.opponent and uInvade.opponent['uid']:
        invade_user_instance.add_user(uInvade.opponent['uid'])
    uInvade.set_opponent(opponent_info)
    return api_info()


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
    # 消耗体力
    need_stamina = uInvade._common_config['invade_fight_stamina']
    tools.del_user_things(uInvade, 'stamina', need_stamina, 'invade')

    opponent_info = uInvade.opponent
    opponent_uid = opponent_info['uid']
    # 记录战前信息
    umodified = uInvade.user_modified
    umodified.add_dungeon_info('invade', {
        'opponent_info': opponent_info,
    })

    # 如果是虚拟玩家，造一个数据
    if not opponent_uid:
        opponent_team_info = {
                    'lv': 10,
                    'nature_0': 5,
                    'nature_1': 5,
                    'nature_2': 5,
                    'nature_3': 5,
                    'nature_4': 5,
                    'nature_5': 5,
                    'team': uInvade._userInit_config['init_team'],
                    'card_lv': [2, 4, 6, 8],
                    'card_favor':[0, 1, 0, 1],
                }
    else:
        opponent_invade = UserInvade.get(opponent_uid)
        opponent_team_info = opponent_invade.watch_team_info()
    # 每次打别人， 自己的保护时间取消
    invade_user_instance = InvadeUser.get_instance()
    uInvade.reset_shield_time()
    invade_user_instance.add_user(uInvade.uid)
    # 重置 连续寻找对手次数 清空已找到对手
    uInvade.reset_refresh_cnt()
    uInvade.clear_opponent()
    return {'enemy': opponent_team_info}
    

def api_end_invade(win=True):
    """ api/invade/end_invade
    战斗胜利
    Argvs:
        win(bool): 是否胜利
    Returns:
        exp(int): 获得经验
        cup(int): 获得奖杯数，可为负数
        coin(int): 获得金币数
    """ 
    user = request.user
    common_config = user._common_config
    umodified = user.user_modified
    start_info = umodified.clear_dungeon_info('invade')

    now = int(time.time())
    if now - start_info['time'] <= 1:
        raise LogicError("rush a dungeon to quick") 

    uInvade = user.user_invade
    uProperty = uInvade.user_property
    opponent_info = start_info['opponent_info']
    opponent_uid = opponent_info['uid']
    opponent_invade_log = {
        'status': 0,
        'name': user.name,
        'uid': user.uid,
        'lv': uProperty.lv, 
        'cup': uInvade.cup,
        'time': int(time.time()),
    }
    opponent_invade_log['team_info'] = uInvade.now_team_info()
    # 胜利获得全额经验1奖杯和对手金钱;失败扣奖杯,且对手加代币
    full_exp = common_config['invade_fight_exp']
    if win:
        # 连胜次数加1
        uInvade.inc_consecutive_win()
        award = opponent_info['win_award']
        award['exp'] = full_exp
        opponent_invade_log['status'] = 0
        opponent_invade_log['lose_coin'] = award.get('coin', 0)
    else:
        # 失败清空连胜次数 
        uInvade.reset_consecutive_win()
        award = opponent_info['lose_award']
        award['exp'] = full_exp // 3
        opponent_invade_log['status'] = 1
        opponent_invade_log['win_invade_jeton'] = 1

    # 改变对手数据！ 加代币 或 减钱
    if opponent_uid:
        opponentInvade = UserInvade.get(opponent_uid)
        # 日志中主城设为被打者主城
        opponent_invade_log['capital_city'] = opponentInvade.user_cities.capital_city
        # 要告诉对手他别打了
        opponentInvade.add_history(opponent_invade_log)
        invade_user_instance = InvadeUser.get_instance()
        if win:
            opponent_coin = opponentInvade.user_property.coin 
            award['coin'] = min(opponent_invade_log['lose_coin'], opponent_coin) 
            tools.del_user_things(opponentInvade, 'coin', award['coin'], 'beinvaded')
            # 给被打人 加护盾时间
            shield_gap = common_config['invade_keep_shield_seconds']
            shield_time = int(time.time()) + shield_gap
            invade_user_instance.add_user(opponent_uid, shield_time) 
            opponentInvade.reset_shield_time(shield_time)
        else:
            invade_user_instance.add_user(opponent_uid) 
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

    # 消耗体力
    need_stamina = uInvade._common_config['invade_defense_stamina']
    tools.del_user_things(uInvade, 'stamina', need_stamina, 'invade')
    # 记录战前信息
    umodified = uInvade.user_modified
    umodified.add_dungeon_info('invade_defense', {
        'history': defe_history,
    })
    # 清除此次日志
    uInvade.clear_history(index=history_index)
    return {'enemy': defe_history['team_info']}


def api_end_defense(win=True):
    """ api/invade/end_defense
    结束反击战斗
    
    """ 
    user = request.user
    full_exp = user._common_config['invade_defense_exp']
    if not win:
        # 反击失败只给1/3经验
        return {'award': {'exp': full_exp // 3}}
    umodified = user.user_modified
    defe_history = umodified.get_dungeon_info('invade_defense')['history']
    umodified.clear_dungeon_info('invade_defense')
    now = int(time.time())
    if now - defe_history['time'] <= 1:
        raise LogicError("rush a dungeon to quick") 

    uInvade = user.user_invade
    award = {
        'exp': full_exp,
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
    return {'awards': {'coin': 10 }}

