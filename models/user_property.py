#-*- coding: utf-8 -*-

from libs.model import BaseModel
from models import GameModel


class UserProperty(GameModel):
    def __init__(self, uid=None):
        self.uid = uid
        self.exp = 0
        self.stamina = 0
        self.diamond = 0
        self.money = 0
        self.coin = 0
        self.heroSoul = 0
        self.master_0 = 0       # 元素掌握度
        self.master_1 = 0       # 元素掌握度
        self.master_2 = 0       # 元素掌握度
        self.master_3 = 0       # 元素掌握度
        self.master_4 = 0       # 元素掌握度
        self.master_5 = 0       # 元素掌握度
        self.master_remain = 0      # 剩余元素掌握度

        
    def add_thing(self, thing, num):
        old_num = getattr(self, thing)
        new_num = max(old_num + num, 0)
        setattr(self, thing, new_num)
        Umodified = self.user_modified 
        Umodified.modified[thing] = new_num
        Umodified.put()
        self.put()
        
        return new_num
            
        
