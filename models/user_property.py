#-*- coding: utf-8 -*-

from libs.model import BaseModel


class UserProperty(GameModel):
    def __init__(self, uid):
        super(UserBase, self).__init__()
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

    @classmethod
    def get_or_create(self, uid):
        return 
        
        
