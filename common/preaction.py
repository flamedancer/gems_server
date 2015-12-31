# -*- coding: utf-8 -*-
"""
api 请求的验证，初始化，和收尾工作

client 用post请求服务器
client post 数据唯一字段data, value为json格式str, 所含key如下:
uid  玩家id  str
timestamp 客户端请求时间 int
剩余为 游戏逻辑所需字段  
例:
     data={"uid":"memme",
     "timestamp":"1435833203.454141",
     "last_update_time":"0"}



server 返回json数据
error_code 错误代号,可无 int
error_msg 错误信息,可无 str 
timestamp 服务器返回数据时间 int 
update_userInfo  玩家更新数据 dir
data 游戏逻辑所需字段  
例:
    {"update_userInfo": {"money": 1500}, "timestamp": {}, "data": {"update_configs": {}}, "uid": {}}

"""

import os
import json
import time
import random
import datetime
import md5
from libs.dbs import app 
from common.exceptions import *
from common.utils import print_err
from bottle import request
from models.user_base import UserBase
import settings


def prelogic(func):
    def wrap_func(*args, **kargs):
        result = {}
        result['timestamp'] = int(time.time())
        try:
            data = request.forms.get('data')
            captcha = request.forms.get('captcha', None)
            captcha_validation(captcha, data)
        
            print data
            data = json.loads(data)
            
            timestamp = data.pop('timestamp')
            timestamp_validation(timestamp)
            uid = data.pop('uid', None)
            signature_validation(uid)
            request.api_data = data
            result['data'] = func(*args, **kargs)
        except Error as e:
            app.pier.clear()
            result['error_code'] = e.error_code
            result['error_msg'] = e.error_msg
            return result
        except Exception as e:
            app.pier.clear()
            print_err()
            result.update({
                'error_code': 4,
                'error_msg': 'system erro!'
            })
            return result
        result['uid'] = request.user.uid
        result['update_userInfo'] = update_user_data()
        app.pier.save()
        print "debug_return", result
        return result
    return wrap_func


def captcha_validation(captcha, data):
    check_code = settings.CHECK_CODE
    #local_arg = md5.md5((data + check_code).encode('utf-8')).hexdigest()[:10]
    local_arg = md5.md5((data + check_code)).hexdigest()[:10]
    print "md5 origin", data + check_code
    print "md5 check", local_arg
    if local_arg != captcha:
        raise SignatureError
        print "debug captcha error local capt", local_arg, captcha 

    
def timestamp_validation(timestamp):
    pass


def signature_validation(uid):
    print "signatur_uid", uid
    # 如果没有uid, 新建
    if not uid:
        uid = 'test' + "{:0>6}".format(random.randrange(100000000))
    user = UserBase.get_no_none(uid)
    user.put()
    request.user = user

def pier_clear():
    app.pier.clear()


def update_user_data():
    Umodified = request.user.user_modified
    update_data = Umodified.modified
    if update_data:
        Umodified.modified = {}
    update_data['flags'] = Umodified.get_flags()
    update_data['guide_flags'] = Umodified.guide_flags
    return update_data

