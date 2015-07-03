#-*- coding: utf-8 -*-

from bottle import request
from models.user_base import UserBase 
from common.tools import add_user_things
from common.game_config import get_config_update_time
from common.game_config import get_config_str
from common.game_config import NEED_SYNC_CONFIGS


def api_login():
    print "get me"

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
    result = {}
    Ubase = request.user
    add_user_things(Ubase, 'money', 100, 'login')
    result['update_configs'], result['last_update_time'] = get_update_config(int(last_update_time))
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

