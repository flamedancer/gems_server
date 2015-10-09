# -*- coding: utf-8 -*-
""" 竞技场逻辑
"""

from bottle import request
from common.exceptions import *
from common.arena_user import ArenaUser
from logics import gacha


def api_check_arena():
    """ api/arena/check_arena
    检查竞技状态
    提供当前竞技信息(已选到第几张卡等)
    Returns:
        step(int): 当前竞技场状态 0未开启 1选第一张卡 2选第二张卡...  5准备开始竞技 6完成竞技等待领取奖励 
        selected_cards(list): 已选的卡,长度为4,未选的位为空字符串      
        cards_pool(list): 备选的卡
        win(int): 已胜场数
        lose(int): 已负场数

        例:{
            'step': 3,
            'selected_cards': ['1_card', '3_card', '', ''],
            'cards_pool': [ ['1_card', '10_card', '11_card'], 
                            ['3_card', '30_card', '33_card'],
                            ['5_card', '50_card', '6_card'],
                            ['8_card', '9_card', '7_card'],
                          ],
            'win': 0,
            'lose': 0,
        }
    """
    uarena = request.user.user_arena
    # 是否结束竞技, 胜10或负2
    if uarena.win >= 10 or uarena.total - uarena.win >= 2:
        uarena.set_step(6)
    return uarena.pack_info()


def api_new_arena():
    """ api/arena/new_arena
    开启新的竞技场
    Returns:
        cards_pool(list): 此次竞技候选卡
    """
    uarena = request.user.user_arena
    if uarena.is_in_arena():
        raise LogicError('Aready in arena') 
    
    team_length = uarena._common_config['team_length']
    cards_pool = []
    for cnt in range(team_length):
        cards_pool.append(gacha.gacha('diamond_gacha'))
    uarena.set_cards_pool(cards_pool) 
    uarena.set_step(1)
    return {'cards_pool': cards_pool}


def api_select_card(step, card_id):
    """ api/arena/select_card
    玩家选卡
    Args:
        step(int): 选卡步骤数  1选第一张卡 2选第二张卡...
        card_id(str): 此次选择的卡片id
    """
    uarena = request.user.user_arena
    team_length = uarena._common_config['team_length']
    if step not in range(1, 1 + team_length):
        raise ParamsError('Step num error')
    index = step - 1
    cards_pool = uarena.cards_pool
    if card_id not in cards_pool[index]:
        raise ParamsError('Has no this card in pool')
    uarena.select_card(index, card_id)
    uarena.set_step(step + 1)
    return {}


def api_start_fight():
    """ api/arena/start_fight
    开打
    Returns:
        enemy(dict):
            uid: 敌人uid
            name: 敌人名字
            lv: 敌人等级
            nature_*: 敌人各元素掌握度
            team: 敌人卡片队伍
    """
    uarena = request.user.user_arena
    if not self.can_fight():
        raise LogicError('Cannot fight')
    uarena.inc_total()
    except_uids = uarena.has_fight_uids + [uarena.uid]
    enemey_info = ArenaUser.get_random_user(except_uids=excep_uids)
    ArenaUser.add_user(uarena.uid, uarena.selected_cards)
    return {'enemy': enemy_info}


def api_end_fight():
    """ api/arena/end_fight
    战斗胜利
    """ 
    uarena = request.user.user_arena
    uarena.inc_win()
    return {}


def api_cancel_arena():
    """  api/arena/cancel_arena
    取消这次竞技
    """
    uarena = request.user.user_arena
    uarena.set_step(0)
    return {}

def api_get_award():
    """ api/arena/get_award
    领取竞技奖励
    """
    awards = {
        'coin': 20,
    }
    return {'awards': awards}
