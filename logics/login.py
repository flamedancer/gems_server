#-*- coding: utf-8 -*-
"""
    玩家登入逻辑
"""


from bottle import request
from models.user_base import UserBase 
from common.tools import add_user_things
from common.game_config import get_config_update_time
from common.game_config import get_config_str
from common.game_config import get_config_dir
from common.game_config import NEED_SYNC_CONFIGS



# def login(request):
#     print "#####test dir request.forms::", dir(request.forms)
#     uid = str(request.forms.get('uid', ''))
#     print uid
#     # test list
#     list_data = request.forms.get('list_data')
#     print "#####test list_data:: by get", list_data 
#     list_data = request.forms.getlist('list_data')
#     print "#####test list_data:: by getlist", list_data 
# 
#     list_data = request.forms.getall('list_data')
#     print "#####test list_data:: by getall", list_data 
# 
#     # test dir
#     dir_data = request.forms.get('dir_data')
#     print "#####test dir_data:: by get", dir_data 
#     dir_data = request.forms.getall('dir_data')
#     print "#####test dir_data:: by getall", dir_data 
# 
#     # test normal
#     uid_data = request.forms.get('uid')
#     print "#####test uid_data:: by get", uid_data 
#     uid_data = request.forms.getall('uid')
#     print "#####test uid_data:: by get", uid_data 
# 
# 
#     print "#####test allvalues:: values", request.forms.values() 
#     print "#####test allvalues:: items", request.forms.items() 
# 
#     print "###### test dict", request.forms.dict
#     print "###### test dict", request.forms.allitems()
#     Ubase = UserBase.get(uid)
#     if not Ubase:
#         print "create new uid", uid
#        
#             
#         Ubase = UserBase.create(uid)
#         Ubase.put()
#     add_user_things(Ubase, 'money', 100, 'login')
#     Ucards = Ubase.user_cards
#      
#         
# 
#     return Ucards.__dict__ 
# 
#     Ubase = UserBase.get(uid)
#     if not Ubase:
#         print "create new uid", uid
#        
#             
#         Ubase = UserBase.create(uid)
#         Ubase.put()
#     Uproperty = Ubase.user_property
#     #Uproperty.add_thing('money', 100)
#         
# 
#     return Uproperty.__dict__ 

def api_login(last_update_time):
    """  api/login/login

    游戏开始，先获取游戏基本数据，
    包括玩家基本数据和变动的配置
    Args:
        last_update_time(int): 客户端本地配置最后更新时间
    Returns:
        user_info(dict): 玩家基本数据, 见function user_info:
        update_configs(dict): 需要客户端更新的配置
        last_update_time(int): 服务端配置最后更新时间
            如果为0，代表没有需要更新的配置
    """
    result = {}
    Ubase = request.user
    add_user_things(Ubase, 'money', 100, 'login')
    result['user_info'] = get_user_info(Ubase)
    update_configs, update_time = get_update_config(int(last_update_time))
    if update_time:
        result['update_configs'], result['last_update_time'] = update_configs, update_time
        if 'card_config' in result['update_configs']:
            result['all_card_len'] = len(result['update_configs']['card_config'])
    return result
    


def get_update_config(last_update_time):
    update_configs = {}
    new_last_update_time = 0
    for config_name in NEED_SYNC_CONFIGS:
        this_config_update_time = get_config_update_time(config_name)
        if this_config_update_time > last_update_time:
            update_configs[config_name] = get_config_str(config_name)    
            if this_config_update_time > new_last_update_time:
                new_last_update_time = this_config_update_time 
    return update_configs, new_last_update_time


def get_user_info(uBase):
    user_info = {}
    user_info.update(uBase.to_dict())
    user_info.update(uBase.user_property.to_dict())
    user_info.update(uBase.user_cards.to_dict())
    return user_info
    
