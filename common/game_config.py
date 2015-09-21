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
            ('language_config', u'前端语言包'),
         ],
    },
    {
        'category': u'主角',
        'content':[
            ('userInit_config', u'主角初始配置'),
            ('userlv_config', u'主角等级配置'),
         ],
    },
    {
        'category': u'卡牌',
        'content':[
            ('card_config', u'卡牌基本配置'),
            ('update_config', u'升级消耗英魂'),
            ('gacha_config', u'抽卡配置'),
            ('cardother_config', u'开城|分解'),
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
]

NOTE = {
    'userlv_config': \
u'''
主角成长属性增加
1.key为等级
2.value为：
        'exp':0,            # 升级到此等级需要经验
        'lv_add_stamina':0, # 升级到此等级时送的经验,可超过上限
        'stamina':30,       # 体力上限

''',

    'update_config': \
u'''
1.卡片升级只消耗英魂,消耗数和卡片品质和升的等级有关
2.key为品质id, value 为长度15的数组,
3.value的index为等级数,对应项为需消耗的英魂


''',

    'cardother_config': \
u'''
开城消耗金币配置open_city_consume_coin
1.开城消耗金币，根据已开城数计算
2.数组index为已开城数，对应项为需要金币数


分解卡片dismiss_prod_heroSoul
1.分解所得英魂值只与卡牌的品质有关
2.key为品质id, value 为所得英魂数量
3. '0'普通
   '1'精良
   '2'稀有
   '3'史诗
   '4'传说

''',

}


NEED_SYNC_CONFIGS = [
    'common_config',
    'language_config',
    'card_config',
    'update_config',
    'cardother_config',
    'skill_config',
    'city_config',
    'conquer_config',
    'conversation_config',
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
