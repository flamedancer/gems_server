#-*- coding: utf-8 -*-
"""
    玩家登入逻辑
"""

import json
from bottle import request
from models.user_base import UserBase 
from common.tools import add_user_things
from common.game_config import get_config_update_time
from common.game_config import get_config_str
from common.game_config import get_config_dir
from common.game_config import NEED_SYNC_CONFIGS


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
            [
              {
                "status": 2, # 卡片状态 0 未拥有  1 可召唤 2 已拥有 
                "wrap_defense":0.2,
                "race":1,
                "attack":[
                    2,
                    3,
                    3,
                    3,
                    4,
                    4,
                    4,
                    5,
                    5,
                    6,
                    6,
                    6,
                    7,
                    7,
                    8
                ],
                "f_maxmp":8,
                "type":[
                    2
                ],
                "words_2":"你这是自寻死路",
                "stun_defense":0.2,
                "skill":[
                    "1_skill",
                    "300_skill",
                    "301_skill",
                    "302_skill"
                ],
                "picture":"1_card.png",
                "id":"1_card",
                "description":"希腊神话中的怪物。外形为双头犬,且尾巴是一条蛇,在“日落之岛”上负责看守牛群。英雄赫拉克勒斯在完成其十件任务的过程中将它杀死。",
                "attack_type":0,
                "myth":1,
                "maxmp":[
                    1,
                    1,
                    1,
                    1,
                    1,
                    2,
                    2,
                    2,
                    2,
                    3,
                    4,
                    4,
                    5,
                    5,
                    6
                ],
                "hp":[
                    3,
                    3,
                    3,
                    4,
                    4,
                    4,
                    5,
                    5,
                    5,
                    5,
                    5,
                    6,
                    6,
                    7,
                    7
                ],
                "lv":1,
                "defense":[
                    1,
                    1,
                    2,
                    3,
                    3,
                    4,
                    5,
                    5,
                    6,
                    6,
                    7,
                    7,
                    8,
                    8,
                    8
                ],
                "frozen_defense":0.2,
                "camp":0,
                "burn_defense":0.2,
                "name":"欧特鲁斯",
                "quality":0,
                "words_1":"已经不在是恶魔或是精灵,甚至已经不知是什么生物",
                "poison_defense":0.2,
                "favor":0,
                "silence_defense":0.2
                  }, 
                 .......
               ]


        last_update_time(int): 服务端配置最后更新时间
            如果为0，代表没有需要更新的配置
    """
    result = {}
    ubase = request.user
    add_user_things(ubase, 'money', 100, 'login')
    result['user_info'] = get_user_info(ubase)
    update_configs, update_time = get_update_config(int(last_update_time))
    if update_time:
        result['update_configs'], result['last_update_time'] = update_configs, update_time
    #result['all_cards'] = get_all_cards_info(ubase)
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
    user_info.update(ubase.user_cards.to_dict())
    user_info.update(get_user_cardinfo(ubase))
    return user_info

def get_user_cardinfo(ubase):
    cards_info = ubase.user_cards.to_dict()
    
    # 调整user_cards 格式
    new_cards_list = []
    for card_id in cards_info['cards']:
        card = {}
        card['id'] = card_id
        card.update(cards_info['cards'][card_id])
        new_cards_list.append(card)
    cards_info['cards'] = new_cards_list
    return cards_info
   
    
