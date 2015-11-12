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
         例如:
            {'cards': {'10_card': {'exp': 0, 'favor': 0, 'lv': 0, 'num': 1},
                       '1_card': {'exp': 0, 'favor': 0, 'lv': 0, 'num': 1},
                       '43_card': {'exp': 0, 'favor': 0, 'lv': 0, 'num': 1},
                       '7_card': {'exp': 0, 'favor': 0, 'lv': 0, 'num': 1}},
             'city_jeton': 0,
             'cur_team_index': 0,
             'diamond': 0,
             'exp': 0,
             'gender': 'man',
             'heroSoul': 0,
             'lv': 0,
             'money': 1400,
             'name': '',
             'nature_0': 0,
             'nature_1': 0,
             'nature_2': 0,
             'nature_3': 0,
             'nature_4': 0,
             'nature_5': 0,
             'nature_remain': 0,
             'picture': 1,
             'pk_jeton': 0,
             'stamina': 0,
             'subpicture': 0,
             'teams': [['1_card', '7_card', '10_card', '43_card'], [], []],
             'uid': '333333111',
             'vip_lv': 0}


        update_configs(dict): 需要客户端更新的配置

         例如卡牌配置:
             卡牌配置: "card_config": {...}
    
        last_update_time(int): 服务端配置最后更新时间
            如果为0，代表没有需要更新的配置
    """
    result = {}
    ubase = request.user
    card_config = ubase._card_config
    result['user_info'] = get_user_info(ubase)
    update_configs, update_time = get_update_config(int(last_update_time))
    if update_time:
        result['update_configs'], result['last_update_time'] = update_configs, update_time
        print "#####COnfig_keys:", result['update_configs'].keys()
    # 城市进贡
    prod_city_award(ubase)
    # 登入奖励
    result['login_awards'] = get_login_award(ubase)
    # 登入游戏时不需要发已修改的信息, 只留 红点标记
    umodified = ubase.user_modified
    umodified.modified = get_flags(ubase)
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

def get_flags(ubase):
    return {"flags": {}}

    
def get_login_award(ubase):
    awards_info = []
    td = datetime.datetime.today()
    # 新玩家第一次登入
    if not ubase.last_login_date:
        ubase.record_login()
        return awards_info
    today_first_login = ubase.record_login()
    if not today_first_login:
        return awards_info
    awards_info.append(get_capital_award(ubase))
    awards_info.append(get_invade_award(ubase))
    # 城市代币产出不在奖励弹框显示
    get_city_jeton(ubase)
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
    return {'type':  'captial',
            'award': award,
    }


def get_invade_award(ubase):
    uinvade = ubase.user_invade
    td =  datetime.datetime.today() 
    # 平日发普通奖励，第七天发终极奖励 并重置城战
    sevent_day = ubase._common_config['invade_seventh_weekday']
    
    # 和上次登入是否同一周 若不是 重置
    if total_isoweek(stamp=ubase.last_login_time, start=sevent_day) != (
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
    return {'type': 'invade',
            'award': award,
    }


def get_pvp_award(ubase):
    upvp = ubase.user_pvp
    td = datetime.datetime.today()
    # 每双周结算奖励
    award_day = ubase._common_config['pvp_award_weekday']
    # 和上次登入是否同一双周 若不是 重置
    last_day = datetime.date.fromtimestamp(ubase.last_login_time)
    last_week = total_isoweek(stamp=ubase.last_login_time, start=award_day)
    this_week = total_isoweek(start=award_day)
    # 超过一个双周重置一次
    if (this_week / 2) - (last_week / 2) == 1:
        upvp.reset_pvp()
    # 超过二个双周重置两次成初始
    elif (this_week / 2) - (last_week / 2) >= 2:
        upvp.reset_pvp()
        upvp.reset_pvp()
    # 此周为双周 且为发放奖励的日子
    is_award_day = this_week % 2 == 1 and td.isoweekday() == award_day 
    if not is_award_day:
        return {}
    pvpaward_config = ubase._pvpaward_config
    pvp_grade = str(upvp.grade)
    award = pvpaward_config.get(pvp_grade, {})
    if not award:
        return {}
    add_user_awards(ubase, award, 'login_pvp')
    return {'type': 'pvp',
            'award': award,
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


def prod_city_award(ubase):
    """ 产出城市进贡 """
    td = datetime.datetime.today()
    ucities = ubase.user_cities
    last_datetime = datetime.datetime.fromtimestamp(ubase.last_login_time)
    # 每小时产出一次
    if str(last_datetime)[:13] == str(td)[:13]:
        return
    # 有未领取的进贡不产生新的进贡
    if ucities.city_award:
        return
    award = {}
    city_config = ubase._city_config
    # 每个征服了的城市都有进贡几率
    for city_id in ucities.cities:
        if not ucities.has_conquer_city(city_id):
            continue
        # 每一级都增加1%的进贡率 
        if random.random() > (0.01 * ucities.cities[city_id]['lv']):
            continue
        # 贡品类型
        award_type = city_config[city_id]['reward_type']
        # 城市声望越高，贡品的数量越多
        award_num = city_config[city_id]['reward_num'][ucities.cities[city_id]['reputation_lv']]
        award.setdefault(award_type, 0)
        award[award_type] += award_num
    ucities.set_city_award(award)
         

