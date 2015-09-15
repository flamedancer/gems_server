#-*- coding: utf-8 -*-

from libs.model import BaseModel
from models import GameModel
from common.exceptions import *


class UserProperty(GameModel):
    def __init__(self, uid=None):
        self.uid = uid
        self.exp = 0           # 经验值
        self.topfull_exp = self.get_topfull_exp()   # 当前等级最大经验
        self.lv = 1            # 玩家等级
        self.vip_lv = 0        # vip 等级
        self.stamina = 0       # 体力值
        self.diamond = 0       # 钻石
        self.coin = 0         # 金币 
        self.pk_jeton = 0      # 天梯代币  
        self.heroSoul = 0      # 英魂数量
        self.nature_0 = 0       # 蓝元素掌握度
        self.nature_1 = 0       # 红元素掌握度
        self.nature_2 = 0       # 绿元素掌握度
        self.nature_3 = 0       # 褐元素掌握度
        self.nature_4 = 0       # 黄元素掌握度
        self.nature_5 = 0       # 紫元素掌握度
        self.nature_remain = 0      # 剩余元素掌握度

    @classmethod
    def create(cls, uid):
        obj = cls(uid)
        obj.init()
        obj.put()
        return obj

    def init(self):
        init_property = self._userInit_config.get('init_property', {})
        self.__dict__.update(init_property)

    def get_topfull_exp(self):
        return self.exp * 2 + 1

    def add_thing(self, thing, num):
        old_num = getattr(self, thing)
        new_num = max(old_num + num, 0)
        setattr(self, thing, new_num)
        self.put()
        return new_num

    def del_thing(self, thing, num):
        old_num = getattr(self, thing)
        new_num = old_num - num  
        if new_num < 0:
            raise LackError('Not enough thing')
        setattr(self, thing, new_num)
        self.put()
        return new_num
        
