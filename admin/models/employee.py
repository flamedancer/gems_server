# -*- coding: utf-8 -*-

import hashlib
import datetime
from libs.model import MongoModel

class Employee(MongoModel):
    pk = 'username'

    def __init__(self):
        self.username = "" # 管理员账号
        self.realname = "" # 管理员真实姓名
        self.password = "" # 管理员密码
        #self.email = "" # 邮件
        self.role = '' # 角色
        self.last_ip = "0.0.0.0"
        self.register_time = datetime.datetime.now()
        self.last_login_time = datetime.datetime.now()
        self.permissions = [] # 管理员可用权限
        self.in_review = False #帐号注册true为等待审核通过，false为通过审核
        self.new_permissions = [] # 

    def set_password(self, password):
        self.password = hashlib.md5(password).hexdigest() 

    def check_password(self, password):
        return self.password == hashlib.md5(password).hexdigest()
