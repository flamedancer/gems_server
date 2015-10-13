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
        ],
    },
    {
        'category': u'物品',
        'content':[
            ('prop_config', u'道具配置'),
         ],
    },
]

NOTE = {
    'common_config':\
u'''
***一些游戏基础配置***


卡牌最高等级max_card_lv

城市最高等级max_city_lv

城市最高声望值max_city_reputation

卡牌编队最大长度team_length


开城消耗金币配置open_city_consume_coin
1.开城消耗金币，根据已开城数计算
2.数组index为已开城数，对应项为需要金币数

开启竞技场需要金币open_arena_coin
每场竞技战斗消耗体力arena_fight_stamina
竞技场对手卡牌好感度arena_card_favor
竞技场对手卡牌等级arena_card_lv


''',
    'userlv_config': \
u'''
***主角等级成长***


主角成长属性增加
1.key为等级
2.value为：
        "exp":0,            # 升级到此等级需要经验
        "lv_add_stamina":0, # 升级到此等级时送的体力,可超过上限
        "stamina":30,       # 此等级体力上限
3.以下为例, 玩家升级到2级需要总经验10;当升到2级时，直接增加1体力值，
  同时体力上限变更为50

4.例：
{
  "1": {
        "exp":0,
        "lv_add_stamina":0,
        "stamina":30,
  },
  "2": {
        "exp":10,
        "lv_add_stamina":1,
        "stamina":50,
  },
 ......
}

''',

    'cardup_config': \
u'''
***卡牌养成有关配置***
卡牌品质分为：普通卡（白）、精良卡（绿）、稀有卡（蓝）、史诗卡（紫）、传说卡（橙）。


卡牌升级消耗英魂配置 lvup_consume_heroSoul
1.卡片升级只消耗英魂,消耗数和卡片品质和升的等级有关
2.key为品质id, value 为长度14的数组,
3.value的index为等级数,对应项为当前等级升到下一等级需消耗的英魂
  按下配置为例，普通卡当前为8级，则它升到9级需花费8英魂
4.例如：
"lvup_consume_heroSoul":{
   "0": [1,2,3,4,5,6,7,8,9,10,11,12,13,14],
   ......
}


分解卡片产生英魂配置dismiss_product_heroSoul
1.分解所得英魂值只与卡牌的品质有关
2.key为品质id, value 为所得英魂数量
3. '0'普通
   '1'精良
   '2'稀有
   '3'史诗
   '4'传说
4.例:
"dismiss_product_heroSoul":{
    "0": 4,
    ......
}


卡牌召唤 品质系数配置 summon_coe
1.卡牌召唤和品质、等级、好感度有关
2.所需金币=品质系数+200*(当前等级-1)+800*当前好感度,好感度=0、1、2、3
3.品质系数key 为品质id,value为系数
4.例:
"summon_coe":{
   "0": 1,
   "1": 2,
   ......
}

''',

    'gacha_config':\
u'''
***抽奖配置***


1.分为金币抽卡和钻石抽卡,消耗对应抽卡包
2.分为两层:
   第一层key为品质id；
   第二层key为唯一标示符，value为具体物品信息
3.第二、三层都有个特殊的字段 weight, 代表外围属性权重
4.金币抽字段为 coin_gacha ;  元宝抽为  diamond_gacha
5.以下为例，看看出：
    1.抽到 品质1的概率为 25% = (10 / (10 + 30))
    2.抽到5001_card 的概率为 1/16  = (  25% * (5 / (5 + 5 +10 )) )
    
5.例：
"diamond_gacha":{
        "1":{
              "1":{
                  "id":"5001_card",
                  "weight":5,
              },
              "2":{
                  "id":"5002_card",
                  "weight":5,
              },
              "3":{
                  "id":"5003_card",
                  "weight":10,
              },
              "weight": 10,
           },
        "2":{
            "1":{
                "id":"4001_card",
                "weight":10,
            },
            "2":{
                "id":"4002_card",
                "weight":10,
            },
            '3':{
                "id":"4003_card",
                "weight":10,
            },
            "weight": 30,
        },
}
''',
    'conquer_config':\
u'''
key  (城市id)                   
    key  （floor_index）                
        name    str 关卡名字    
        stamina int 消耗体力    
        award   dict    战场掉落    
        enemy    list    敌将以及基础等级    
        enemy_nature    int 对手全元素掌握度    
        enemy_favor int 敌将好感度  
                    
                    
                    
例如：                  
{ "0": {                    
    "1": {              
        "name": "第一关"，          
        "stamina"： 10，            
        "enemy"：[["1_card",1], ["3_card",2],["5_card",3], ["9_card",4]],           
        "enemy_nature": 3,          
        "enemy_favor": 1,           
        "award": {          
            "card": [  ["1_card", 1],  ["2_card", 2],…..], # [ [卡牌id, 数量], ..
            "prop": [  ["1_prop", 1],  ["2_prop", 2],…..],
            "exp": 10,      
            "coin": 10,     
            "heroSoul",     
            "diamond": 1,       
        },          
    },              
    "2": {              
    ……              
    ……              
    ……              
''',
    'conversation_config':\
u'''
        字段    类型    解释                
                                
key  (城市id)                               
    key  （floor_index）                            
        before  list    进场对话
                                 说话者  说话者头像id    语句
                                 self    ""  xxx
                                 npc "1_card"    xxx
                                 enemy   "2_card"    xxx
                                
        after   list    出场对话                
                                
                                
                                
                                
例如：                              
{ "0": {                                
    "1": {                          
        "before":[  ["self",    "", "你是谁"]，         
            ["npc", "1_card",   "我是npc"]，            
            ["self",    "", "..."]，            
            ["npc", "", "xxx"]，            
            ["enemy",   "2_card",   "插标卖耳"]，           
                                
        ],                      
        "after":[                       
        …                       
        …                       
        ..                      
        ],                      
''',
    'challenge_config':\
u'''
            字段    类型    解释    
                        
key  (城市id)                       
    key  （floor_index 大关卡id）                   
        key  （room_index小关卡id）             
            name    str 关卡名字    
            stamina int 消耗体力    
            award   dict    战场掉落    
            enemy   list    敌将以及等级    
            enemy_nature    int 对手全元素掌握度    
            enemy_favor int 敌将好感度  
            ext_award   dict    额外奖励    
            ext_term str 额外奖励条件    
                        a       己方卡牌不可阵亡
                        b*      上阵卡牌必须全部为*阵营 例: b2 全属于尤克特拉希尔城
                        c*      上阵卡牌必须全部带有某属性 例: c2 全有绿元素 
                        d*      上阵卡牌必须包括某某卡牌 例:  d3 阵营要有斯雷普尼尔
                        
                        
例如：                      
{ "0": {                        
    "1": {                  
        "1":{               
            "name": "第一关"，          
            "stamina"： 10，            
            "enemy"：[["1_card",1], ["3_card",2],["5_card",3], ["9_card",4]],           
            "enemy_nature": 3,          
            "enemy_favor": 1,           
            "award": {          
                "reputation", 当前城市声望
                "exp": 10,      
                "coin": 10,     
                "heroSoul",     
                "diamond": 1,       
                "card": [  ["1_card", 1],  ["2_card", 2],…..], # [ [卡牌id, 数量], ..
                "prop": [  ["1_prop", 1],  ["2_prop", 2],…..],
            },          
            "ext_award": {          
                "coin" :3,      
            },          
            "ext_term": "a",
        }               
    },                  
    "2": {                  
    ……                  
    ……                  
    ……                  
''',

    'arenapool_config':\
u'''
1.分为两层:
   第一层key为选第几张阶段（从1开始）；
   第二层key为唯一标示符，value为具体物品信息
2.第三层有个特殊的字段 weight, 代表此卡权重
    
3.例：
{
        "1":{
              "1":{
                  "id":"5001_card",
                  "weight":5,
              },
              "2":{
                  "id":"5002_card",
                  "weight":5,
              },
              "3":{
                  "id":"5003_card",
                  "weight":10,
              },
              "4":{
                  "id":"5003_card",
                  "weight":10,
              },
           },
        "2":{
            "1":{
                "id":"5001_card",
                "weight":10,
            },
            "2":{
                "id":"4002_card",
                "weight":10,
            },
            '3':{
                "id":"4003_card",
                "weight":10,
            },
            '4':{
                "id":"4004_card",
                "weight":10,
            },
        },
    ....
}
''',

    'arenaaward_config': \
u'''
1.key 为赢了几场 value为具体奖励
2.例:
{
    "0": {
         "exp": 10,      
         "coin": 10,     
         "heroSoul",     
         "diamond": 1,       
         "1_card": 2     卡牌:数量
         "2_prop"：3     道具：数量
         "stamina": 10,
    },
    "1": {
         "exp": 10,      
         "coin": 10,     
         "heroSoul",     
         "diamond": 1,       
         "1_card": 2     卡牌:数量
         "2_prop"：3     道具：数量
         "stamina": 10,
    },
    ....
}

''',

}


NEED_SYNC_CONFIGS = [
    'common_config',
    'language_config',
    'userlv_config',
    'card_config',
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
