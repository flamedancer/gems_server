# -*- coding: utf-8 -*-
"""
存储角色名字对应uid
"""
from libs.model import MongoModel
import datetime

class Names(MongoModel):
    """
    存储用户名字，名字唯一
    """
    pk = 'name'
    fields = ['uid','name','createtime']
    def __init__(self):
        pass

    @classmethod
    def set_name(cls, uid=None, name=None):
        obj = cls()
        obj.uid = uid
        obj.createtime = str(datetime.datetime.now())
        obj.name = name
        #插入，如果有重复会报异常
        obj.insert()


