#-*- coding: utf-8 -*-

import time
import json
from libs.model import RedisKeyValue
from libs.model import ConfigModel

CONFIG_TITLES = [
    {
        'category': u'系统',
        'content':[
            ('system_config', u'系统配置'),
            ('common_config', u'通用配置'),
         ],
    },
    {
        'category': u'玩家',
        'content':[
            ('userInit_config', u'玩家初始配置'),
         ],
    },
    {
        'category': u'卡牌',
        'content':[
            ('card_config', u'卡牌基本配置'),
            ('update_config', u'卡牌进阶'),
         ],
    },
    {
        'category': u'技能',
        'content':[
            ('skill_config', u'技能基本配置'),
         ],
    },

]


NEED_SYNC_CONFIGS = [
    'card_config',
    'skill_config',
]


UPDATE_TIME_SUFFIX = '_updateTime' 

def get_config_update_time(config_name):
    if not config_name in NEED_SYNC_CONFIGS:
        return
    return RedisKeyValue.get(config_name + UPDATE_TIME_SUFFIX)

def set_config_update_time(config_name):
    if not config_name in NEED_SYNC_CONFIGS:
        return
    return RedisKeyValue.set(config_name + UPDATE_TIME_SUFFIX, int(time.time()))
    

def get_config_dir(config_name):
    return ConfigModel.create(config_name).data

def get_config_str(config_name):
    return json.dumps(get_config_dir(config_name))
