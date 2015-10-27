#-*- coding: utf-8 -*-

from models import GameModel
import datetime


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
        self.birthday = str(datetime.datetime.today())

    def change_name(self, new_name):
        new_name = new_name.decode('utf-8')
        self.name = new_name
        self.put()
        return new_name
    
