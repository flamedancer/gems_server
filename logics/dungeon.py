# -*- coding: utf-8 -*-
""" 战斗
"""

import time
from bottle import request
from logics import card
from common import tools
from common.exceptions import *


def api_start(dungeon_type, city_id, team_index='', new_team=None, floor=''):
    """ api/dungeon/start
    进战场
    1.进战场先扣体力 
    2.进战场会先给1/3经验值
    Args:
        dungeon_type(str): 战斗类型 "conquer"征服模式 "challenge"挑战模式 
        city_id(str): 要打哪个城，城市id
        team_index(str): 选取的城市编队id
        new_team(list->str): 新的战斗卡片队伍
        floor(str): 挑战模式选取的大关卡

    Returns:
        enemy_team(list): 敌将编队
        enemy_lv(list->int): 各敌将等级
        enemy_favor(int): 敌将全好感度
        enemy_nature(int): 敌将全元素掌握度
    """
    result = {}
    if team_index != '' and new_team is not None:
        if set(new_team) == set(['']):
            raise ParmasError('Can\'t set empty team !')
        card.api_set_team(team_index, new_team)
    ubase = request.user
    ucities = ubase.user_cities
    if dungeon_type == 'conquer':
        conquer_config = ubase._conquer_config  
        if not ucities.can_conquer_city(city_id):
            raise LogicError("Can't conquer this city")
        cur_stage = str(ucities.cur_conquer_stage(city_id))
        stage_conf = conquer_config[city_id][cur_stage]
        need_stamina = stage_conf['stamina']
        # 扣体力
        tools.del_user_things(ubase, 'stamina', need_stamina, 'conquer')
        enemy_favor = stage_conf['enemy_favor'] 
        enemy_nature = stage_conf['enemy_nature'] 
        enemy_team = []
        base_enemy_lv = []
        for enemy_cid, lv in stage_conf['enemy']:
            enemy_team.append(enemy_cid)
            base_enemy_lv.append(lv)
        enemy_lv = calcu_enemy_lv(ubase.user_cards, base_enemy_lv)
    elif dungeon_type == 'challenge':
        challenge_config = ubase._challenge_config
        if not ucities.can_challenge_city_floor(city_id, floor):
            raise LogicError("Can't challenge this city floor")
        cur_room = str(ucities.cities[city_id]['challenge'][floor])
        room_conf = challenge_config[city_id][floor][cur_room]
        need_stamina = room_conf['stamina']
        # 扣体力
        tools.del_user_things(ubase, 'stamina', need_stamina, 'challenge')
        enemy_favor = room_conf['enemy_favor'] 
        enemy_nature = room_conf['enemy_nature'] 
        enemy_team = []
        enemy_lv = []
        for enemy_cid, lv in room_conf['enemy']:
            enemy_team.append(enemy_cid)
            enemy_lv.append(lv)
        
    umodified = ubase.user_modified
    umodified.temp['dungeon'] = {
        'type': dungeon_type,
        'time': int(time.time()),
        'city_id': city_id,
        'floor': floor,
    }
    umodified.put()
        
    result = {
        'enemy_team': enemy_team,
        'enemy_lv': enemy_lv,
        'enemy_favor': enemy_favor,
        'enemy_nature': enemy_nature,
    }
    return result


def calcu_enemy_lv(ucards, base_lv):
    """
    A敌将最终等级=MIN(15,A敌将最低等级+MAX(0,B))                            
    A敌将最低等级>=所有敌将平均等级时                           
        B=f(我方卡牌等级总数)-0.5*g(我方卡牌等级总数)，四舍五入，保留到整数                     
    A敌将最低等级<所有敌将平均等级时                            
        B=f(我方卡牌等级总数)+0.5*g(我方卡牌等级总数)，四舍五入，保留到整数                     
                                
    其中    A敌将最低等级，后台配置                     
        所有敌将平均等级=所有敌将等级总和/敌将个数                      
                                
        其中当x<15时，f(x)=0.02*x^2-0.04*x+0.02，g(x)=0                     
        其中当x>=15时，f(x)=0.1*x+2.5，g(x)=0.07*x-1                        
    """
    top_lv = ucards._common_config.get('max_card_lv', 15)
    user_team = ucards.cur_team()
    user_card_lv = [ucards.get_card_lv(cid) for cid in user_team if cid]
    aulv = sum(user_card_lv)
    average = sum(base_lv) * 0.1 / len(base_lv)
    return_lv = []

    if aulv < top_lv:
        F = 0.02*aulv**2-0.04*aulv+0.02
        G = 0
    else:
        F = 0.1*aulv+2.5
        G = 0.07*aulv-1

    for elv in base_lv:
        if elv >= average:
            B = F - 0.5*G
        else:
            B = F + 0.5*G
        B = int(round(B)) 
        return_lv.append(min(top_lv, elv + max(0, B)))
    return return_lv


def api_end(dungeon_type, city_id, win=True, has_dead_mem=True, bout=1):
    """ api/dungeon/end
    结束战斗
    Args:
        dungeon_type(str): 战斗类型 "conquer"征服模式 "challenge"挑战模式 
        city_id(str): 要打哪个城，城市id
        win(bool): 战斗胜利还是失败
        has_dead_mem(bool): 挑战模式战斗过程是否有队员死亡
        bout(bool): 挑战模式战斗使用回合数

    Returns:
        coin(int): 奖励 铜钱
        exp(int): 奖励 经验
        diamond(int): 奖励 钻石
        heroSoul(int): 奖励 英魂
        card(list): 奖励 卡牌 [card_id, num]  卡牌id, 数量
            例:
             {
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
        raise LogicError('Should start fight first')
    start_info = umodified.temp['dungeon']
    if start_info.get('type') != dungeon_type or \
       start_info.get('city_id') != city_id:
        raise LogicError('End the wrong fight')
    now = int(time.time())
    if now - start_info['time'] <= 1:
        raise LogicError("rush a dungeon to quick")
    award = {}
    if dungeon_type == 'conquer':
        conquer_config = ubase._conquer_config  
        cur_stage = ucities.cur_conquer_stage(city_id)
        stage_conf = conquer_config[city_id][cur_stage]
        award = stage_conf.get('award', {})

        full_exp = award.get('exp', 0)
        # 失败只加1/3经验 
        if not win: 
            add_exp = int(full_exp / 3)
            tools.add_user_things(ubase, 'exp', add_exp, 'conquer')
            return {'exp': add_exp}
        tools.add_user_awards(ubase, award, 'conquer')
        if str(int(cur_stage) + 1) not in conquer_config[city_id]:
            new_info = ucities.conquer_city(city_id)
        else:
            new_info = ucities.up_conquer_stage(city_id)
        umodified.set_modify_info('cities', new_info)
    elif dungeon_type == 'challenge':
        challenge_config = ubase._challenge_config
        floor = umodified.temp['dungeon']['floor']
        cur_room = str(ucities.cities[city_id]['challenge'][floor])
        room_conf = challenge_config[city_id][floor][cur_room]
        award = room_conf.get('award', {})

        full_exp = award.get('exp', 0)
        # 失败只加1/3经验 
        if not win: 
            add_exp = int(full_exp / 3)
            tools.add_user_things(ubase, 'exp', add_exp, 'challenge')
            return {'exp': add_exp}
        if can_get_ext_award(ubase, room_conf['ext_term'], has_dead_mem, bout):
            for thing, info in room_conf['ext_award'].items(): 
                if thing in award:
                    award[thing] += info
                else:
                    award[thing] = info
        # 加当前城市声望
        if 'reputation' in award:
            add_reputation = award.pop('reputation')
            new_info = ucities.add_city_reputation(city_id, add_reputation)
            umodified.set_modify_info('cities', new_info)
        tools.add_user_awards(ubase, award, 'conquer')
        new_info = ucities.up_challenge_stage(city_id, floor)
        umodified.set_modify_info('cities', new_info)
    umodified.temp.pop('dungeon')
    umodified.put()
    return award
    


def can_get_ext_award(user, ext_term, has_dead_mem, bout):
    """
    a       己方卡牌不可阵亡
    b*      上阵卡牌必须全部为*阵营 例: b2 全属于尤克特拉希尔城
    c*      上阵卡牌必须全部带有某属性 例: c2 全有绿元素 
    d*      上阵卡牌必须包括某某卡牌 例:  d3 阵营要有斯雷普尼尔
    e*      上阵卡牌必须不能带有*属性 例: e2 不能有有绿元素
    f*      上阵卡牌必须全部为*种族 例: f2 全为妖鬼
    g       必须在 <=* 回合内胜利 例: g20 不大于20回合内结束
    """
    card_config = user._card_config
    ucards = user.user_cards
    cur_team = ucards.cur_team()
    for term in ext_term:
        term_name, term_value = term[0], term[1:]
        if term_name == 'a':
            if has_dead_mem:
                return False
        elif term_name == 'b':
            for card_id in cur_team:
                if not card_id:
                    continue
                if card_config[card_id]['camp'] != int(term_value):
                    return False
        elif term_name == 'c':
            term_value = int(term_value)
            for card_id in cur_team:
                if not card_id:
                    continue
                if term_value not in card_config[card_id]['type']:
                    return False
        elif term_name == 'd':
            if term_value + '_card' not in cur_team:
                return False
        elif term_name == 'e':
            term_value = int(term_value)
            for card_id in cur_team:
                if not card_id:
                    continue
                if term_value in card_config[card_id]['type']:
                    return False
        elif term_name == 'f':
            term_value = int(term_value)
            for card_id in cur_team:
                if not card_id:
                    continue
                if term_value != card_config[card_id]['race']:
                    return False
        elif term_name == 'g':
            term_value = int(term_value)
            if term_value > bout:
                return False
    return True
            
        
def api_refresh_challenge_floor(city_id):        
    """ api/dungeon/refresh_challenge_floor
    刷新挑战模式大关卡
    Argvs:
        city_id(str): 需刷新的城市id
    """
    ubase = request.user
    ucities = ubase.user_cities
    #need_coin = ubase._common_config['refresh_challenge_coin']
    #tools.del_user_things(ubase, 'coin', need_coin, 'refresh_challenge_floor')
    new_info = ucities.refresh_challenge(city_id)
    umodified = ubase.user_modified
    umodified.set_modify_info('cities', new_info)
    return {}
        

