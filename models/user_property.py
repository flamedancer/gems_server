#-*- coding: utf-8 -*-

from libs.model import BaseModel
from models import GameModel
from common.exceptions import *
from common.tools import add_user_things


class UserProperty(GameModel):
    def __init__(self, uid=None):
        self.uid = uid
        self.exp = 0           # 经验值
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
        # 初始体力
        init_stamina = self._userlv_config["1"]["stamina"]
        self.stamina = init_stamina
        self.__dict__.update(init_property)
    
    def add_exp(self, num):
        self.exp += num
        userlv_config = self._userlv_config
        old_lv = self.lv
        while str(self.lv + 1) in userlv_config and \
        self.exp >= userlv_config[str(self.lv + 1)]['exp']:
            self.lv += 1
            # 升级体力奖励
            add_stamina = userlv_config[str(self.lv)]['lv_add_stamina']
            add_user_things(self, 'stamina', add_stamina, 'lv_up')

        if str(self.lv + 1) not in userlv_config and \
        self.exp > userlv_config[str(self.lv)]:
            self.exp = userlv_config[str(self.lv)]
        modified = {'exp': self.exp}
        if old_lv != self.lv:
            modified['lv'] = self.lv
            # 升一级加一点剩余元素掌握度 
            modified['nature_remain'] = self.add_thing('nature_remain', 
                self.lv - old_lv)
        self.put()
        return modified            

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
            raise LackError(thing)
        setattr(self, thing, new_num)
        self.put()
        return new_num
        
