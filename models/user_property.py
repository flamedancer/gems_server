#-*- coding: utf-8 -*-

from libs.model import BaseModel
from models import GameModel


class UserProperty(GameModel):
    def __init__(self, uid=None):
        self.uid = uid
        self.exp = 0           # 经验值
        self.lv = 0            # 玩家等级
        self.vip_lv = 0        # vip 等级
        self.stamina = 0       # 体力值
        self.diamond = 0       # 钻石
        self.money = 0         # 金钱 
        self.city_jeton = 0    # 城战代币 
        self.pk_jeton = 0      # 天梯代币  
        self.heroSoul = 0      # 英魂数量
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
        self.put()
        
        return new_num
            
        
