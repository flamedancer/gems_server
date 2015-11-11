#-*- coding: utf-8 -*-

import time
import datetime
from models import GameModel


class UserBase(GameModel):
    """ 玩家基础数据
    """ 
    def __init__(self, uid=''):
        # 玩家 属性数据
        self.uid = uid 
        self.name = ''
        self.gender = 'man' # 性别
        self.picture = 1     # 选择的头像
        self.subpicture = 0  # 玩家选择的皮肤
        self.install_time = '' # 注册时间

        self.last_login_date = '' #  最后登入日期 2015-11-11
        self.last_login_time = 0 #  最后登入时间戳
        self.total_login = 0  # 总共登入天数
        self.consecutive_login = 0 # 连续登入天数

    @classmethod
    def create(cls, uid):
        obj = cls(uid)
        obj.install_time = str(datetime.datetime.today())
        obj.put()
        return obj

    def change_name(self, new_name):
        new_name = new_name.decode('utf-8')
        self.name = new_name
        self.put()
        return new_name

    def record_login(self):
        """ 返回是否当天首次登入 """
        today = datetime.datetime.today()
        # 记录最后登入时间戳
        self.last_login_time = time.time()
        # 不是当天首次登入
        if str(today.date()) == self.last_login_date:
            return False
        # 统计连续登入天数
        if self.last_login_date and (datetime.datetime.strptime(self.last_login_date, "%Y-%m-%d") +
            datetime.timedelta(days=1)).date() == today.date():
            self.consecutive_login += 1
        else:
            self.consecutive_login = 1
        # 当天首次登入 统计总登入天数
        self.total_login += 1
        self.last_login_date = str(today.date())
        return True
