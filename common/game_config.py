#-*- coding: utf-8 -*-

import time
import os
import json
from libs.model import RedisKeyValue
from libs.model import ConfigModel

CONFIG_TITLES = [
    {
        'category': u'系统',
        'content':[
            ('system_config', u'系统配置'),
            ('common_config', u'通用配置'),
            ('language_config', u'前端语言包'),
         ],
    },
    {
        'category': u'主角',
        'content':[
            ('userInit_config', u'主角初始配置'),
            ('userlv_config', u'主角等级配置'),
            ('task_config', u'任务配置'),
         ],
    },
    {
        'category': u'卡牌',
        'content':[
            ('card_config', u'卡牌基本配置'),
            ('cardup_config', u'升级|进阶|分解'),
            ('gacha_config', u'抽卡配置'),
         ],
    },
    {
        'category': u'技能',
        'content':[
            ('skill_config', u'技能基本配置'),
         ],
    },
    {
        'category': u'城市',
        'content':[
            ('city_config', u'城市基础配置'),
            ('conquer_config', u'征服模式配置'),
            ('conversation_config', u'征服对话配置'),
            ('challenge_config', u'挑战模式配置'),
         ],
    },
    {
        'category': u'竞技',
        'content':[
            ('arenapool_config', u'竞技卡池配置'),
            ('arenaaward_config', u'竞技奖励配置'),
            ('invadeaward_config', u'城战奖励配置'),
            ('pvpaward_config', u'天梯奖励配置'),
        ],
    },
    {
        'category': u'物品',
        'content':[
            ('item_config', u'道具配置'),
         ],
    },
]

NEED_SYNC_CONFIGS = [
    'common_config',
    'language_config',
    'userlv_config',
    'card_config',
    'cardup_config',
    'skill_config',
    'city_config',
    'conquer_config',
    'conversation_config',
    'challenge_config',
    'item_config',
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

def get_note(config_name):
    fname = os.path.join("common", "config_docs", config_name + ".txt")
    if not os.path.exists(fname):
        return ''
    with open(fname, 'rb+') as doc_f:
        doc = doc_f.read()
    return doc.decode('utf-8')
        

def save_note(config_name, doc):
    with open(os.path.join("common", "config_docs", config_name + ".txt"),
             'wb+') as doc_f:
        doc_f.write(doc)
    return True
        
