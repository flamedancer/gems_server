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

import sys, os
import json
import time
import random
import datetime
import traceback
from libs.dbs import app 
from common.exceptions import *
from bottle import request
from models.user_base import UserBase


def prelogic(func):
    def wrap_func(*args, **kargs):
        try:
            data = request.forms.get('data')
            print data
            data = json.loads(data) or {} 
            timestamp = data.pop('timestamp')
            timestamp_validation(timestamp)
            uid = data.pop('uid', None)
            signature_validation(uid)
            
            request.api_data = data
            result = {}
            result['data'] = func(*args, **kargs)
        except Error as e:
            result = {}
            result['error_code'] = e.error_code
            result['error_msg'] = e.error_msg
            return result
        except Exception as e:
            print_err()
            return {
                'error_code': 4,
                'error_msg': 'system erro!'
            }
        result['update_userInfo'] = modified_user_data()
        result['uid'] = request.user.uid
        result['timestamp'] = time.time()
        app.pier.save()
        return result
    return wrap_func


def timestamp_validation(timestamp):
    pass


def signature_validation(uid):
    print "signatur_uid", uid
    # 如果没有uid, 新建
    if not uid:
        uid = 'test' + "{:0>6}".format(random.randrange(10000))
    user = UserBase.create(uid)
    user.put()
    request.user = user

def pier_clear():
    app.pier.clear()


def modified_user_data():
    Umodified = request.user.user_modified
    modified_data = Umodified.modified
    if modified_data:
        Umodified.modified = {}
        Umodified.put()
    return modified_data


def print_err():
    sys.stderr.write('=='*30+os.linesep)
    sys.stderr.write('err time: '+str(datetime.datetime.now())+os.linesep)
    sys.stderr.write('--'*30+os.linesep)
    traceback.print_exc(file=sys.stderr)
    sys.stderr.write('=='*30+os.linesep)
