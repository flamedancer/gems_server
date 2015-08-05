#-*- coding: utf-8 -*-
import os

DEBUG = True #False

CURDIR = os.getcwd()


#港台和国服标识
APP_ID = 'cn'
# 数据库地址设置
DB_CONFIG = {
    'cn':{
            'redis':[{'host':'127.0.0.1','port':6379,'db':'2'}],  #一组redis 用来存储游戏数据
            'mongodb':{'host':'127.0.0.1','port':27017,'db':'test_gems','username':'','password':''}, #一个mongodb 用来存储游戏数据
            'top_redis':{'host':'127.0.0.1','port':6379,'db':'3'},  #一个redis 用来做排行榜
            'log_mongodb':{'host':'127.0.0.1','port':27017,'db':'test2_gems','username':'','password':''},   # 一个mongodb 存储log
        },
}

APP_NAME = 'GEMS'

