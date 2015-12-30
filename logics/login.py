#-*- coding: utf-8 -*-
"""
    玩家登入逻辑
"""

import random
import datetime
import json
from bottle import request
from models.user_base import UserBase 
from common.tools import add_user_awards
from common.utils import total_isoweek
from common.game_config import get_config_update_time
from common.game_config import get_config_str
from common.game_config import get_config_dir
from common.game_config import NEED_SYNC_CONFIGS
from logics import invade


def api_login(last_update_time):
    """  api/login/login

    游戏开始，先获取游戏基本数据，
    包括玩家基本数据和变动的配置
    Args:
        last_update_time(int): 客户端本地配置最后更新时间
    Returns:
        user_info(dict): 玩家基本数据, 见function user_info:
        awards(list-dict): 玩家登入奖励
            type: 奖励类型 capital 主城进贡  invade 城战奖励   pvp奖励
            award: 奖励
            
             
        
        例如:

        update_configs(dict): 需要客户端更新的配置

         例如卡牌配置:
             卡牌配置: "card_config": {...}
    
        last_update_time(int): 服务端配置最后更新时间
            如果为0，代表没有需要更新的配置
    """
    result = {}
    ubase = request.user
    # 登入奖励
    result['login_awards'] = get_login_award(ubase)

    result['user_info'] = get_user_info(ubase)
    update_configs, update_time = get_update_config(int(last_update_time))
    if update_time:
        result['update_configs'], result['last_update_time'] = update_configs, update_time
        print "#####COnfig_keys:", result['update_configs'].keys()
    # 登入游戏时不需要发已修改的信息
    umodified = ubase.user_modified
    umodified.modified = {}
    # 检查是否有强退战场，防止未结束
    invade.check_remain_dungeon()
    return result

#def get_all_cards_info(ubase):
#    user_cards = ubase.user_cards.to_dict()
#    all_cards_info = get_config_dir('card_config')
#    for card in all_cards_info:
#        card_id = card['id']
#        # 卡片状态 0 未拥有  1 可召唤 2 已拥有 
#        status = 0
#        if card_id in user_cards:
#            card.update(user_cards[card_id])
#            if card['num'] == 0:
#                status = 1
#            else:
#                status = 2
#        card['status'] = status
#    return all_cards_info


def get_update_config(last_update_time):
    update_configs = {}
    new_last_update_time = 0
    for config_name in NEED_SYNC_CONFIGS:
        this_config_update_time = get_config_update_time(config_name)
        if not this_config_update_time:
            continue
        if this_config_update_time > last_update_time:
            update_configs[config_name] = to_frontend_config(config_name)    
            if this_config_update_time > new_last_update_time:
                new_last_update_time = this_config_update_time 
    return update_configs, new_last_update_time


def dirtolist(old_dict):
    new_list = []
    keys = sorted(old_dict.keys(), cmp=lambda x,y:cmp(int(x.split('_',1)[0]),int(y.split('_',1)[0])))
    for key in keys:
        this_info = {'id': key}
        this_info.update(old_dict[key])
        new_list.append(this_info)
    return new_list


def to_frontend_config(config_name):
    """ 对有些配置进行特殊处理以方便前端解析
    """
    if config_name == 'card_config':
        config_dir = get_config_dir(config_name)
        config_list = dirtolist(config_dir)
        return json.dumps(config_list)
    return get_config_str(config_name)

def get_user_info(ubase):
    user_info = {}
    user_info.update(ubase.to_dict())
    user_info.update(ubase.user_property.to_dict())
    user_info.update(get_user_cardinfo(ubase))
    user_info.update(ubase.user_cities.to_dict())
    user_info.update(ubase.user_items.to_dict())
    return user_info

def get_user_cardinfo(ubase):
    new_cards_info = {}
    cards_info = ubase.user_cards.to_dict()
    new_cards_info.update(cards_info)
    
    # 调整user_cards 格式
    new_cards_info['cards'] = dirtolist(cards_info['cards'])
    return new_cards_info

    
def get_login_award(ubase):
    awards_info = []
    td = datetime.datetime.today()
    # 新玩家第一次登入
    if not ubase.last_login_date:
        ubase.record_login()
        return awards_info
    # 原始上次登入时间
    last_login_time = ubase.last_login_time
    # 修改上次登入时间等
    today_first_login = ubase.record_login()
    if not today_first_login:
        return awards_info
    awards_info.append(get_capital_award(ubase))
    awards_info.append(get_invade_award(ubase, last_login_time))
    awards_info.append(get_pvp_award(ubase, last_login_time))
    # 城市代币产出不在奖励弹框显示
    get_city_jeton(ubase)
    # 清空商城限已购次数
    ubase.user_modified.temp.pop('shop', None)
    awards_info = [award for award in awards_info if award]
    return awards_info

def get_capital_award(ubase):
    """ 主城进贡金币 """
    # 没有主城没有进贡
    if not ubase.user_cities.capital_city:
        return {} 
    lv_conf = ubase._userlv_config[str(ubase.user_property.lv)]
    award = {}
    award['coin'] = lv_conf['reward_coin']
    add_user_awards(ubase, award, 'login_capital')
    language = ubase._language_config['award_msg']['capital']
    return {'type':  'captial',
            'award': award,
            'content1': language['content1'],
            "title": language['title'],
    }


def get_invade_award(ubase, last_login_time):
    uinvade = ubase.user_invade
    td =  datetime.datetime.today() 
    # 平日发普通奖励，第七天发终极奖励 并重置城战
    sevent_day = ubase._common_config['invade_seventh_weekday']
    
    # 和上次登入是否同一周 若不是 重置
    if total_isoweek(stamp=last_login_time, start=sevent_day) != (
        total_isoweek(start=sevent_day)): 
    #if not datetime.datetime.strptime(ubase.last_login_date,
    #    "%Y-%m-%d").strftime("%W") == td.strftime("%W"):
        uinvade.reset_invade()
        
    is_seventh_day = td.isoweekday() == sevent_day 
    invadeaward_config = ubase._invadeaward_config
    cup_rank = str(ubase.user_invade.cup_rank)
    if is_seventh_day:
        award = invadeaward_config['seventh_award'].get(cup_rank, {})
        uinvade.reset_invade()
    else:
        award = invadeaward_config['normal_award'].get(cup_rank, {})
    if not award:
        return {} 
    add_user_awards(ubase, award, 'login_invade')
    language = ubase._language_config['award_msg']['invade']
    return {'type': 'invade',
            'award': award,
            'content1': language['content1'],
            "title": language['title'],
    }


def get_pvp_award(ubase, last_login_time):
    upvp = ubase.user_pvp
    td = datetime.datetime.today()
    # 每双周结算奖励
    award_day = ubase._common_config['pvp_award_weekday']
    # 和上次登入是否同一双周 若不是 重置
    last_day = datetime.date.fromtimestamp(last_login_time)
    last_week = total_isoweek(stamp=last_login_time, start=award_day)
    this_week = total_isoweek(start=award_day)
    # 此周为双周 且为发放奖励的日子
    is_award_day = this_week % 2 == 1 and td.isoweekday() == award_day 
    if not is_award_day:
        return {}
    # 先发奖 再变动段位 
    pvpaward_config = ubase._pvpaward_config
    pvp_grade = str(upvp.grade)
    award = pvpaward_config.get(pvp_grade, {})
    # 超过一个双周重置一次
    if (this_week / 2) - (last_week / 2) == 1:
        upvp.reset_pvp()
    # 超过二个双周重置两次成初始
    elif (this_week / 2) - (last_week / 2) >= 2:
        upvp.reset_pvp()
        upvp.reset_pvp()
    if not award:
        return {}
    add_user_awards(ubase, award, 'login_pvp')
    language = ubase._language_config['award_msg']['pvp']
    return {'type': 'pvp',
            'award': award,
            'content1': language['content1'],
            'content2': language['content2'] % upvp.grade,
            "title": language['title'],
            
    }
    

def get_city_jeton(ubase):
    ucities = ubase.user_cities
    city_config = ubase._city_config
    # 每个征服了的城市都有进贡几率
    for city_id in ucities.cities:
        if not ucities.has_conquer_city(city_id):
            continue
        jeton_num = city_config[city_id]['jeton'][ucities.cities[city_id]['reputation_lv']]
        ucities.add_city_jeton(city_id, jeton_num)

