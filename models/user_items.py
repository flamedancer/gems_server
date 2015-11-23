# -*- coding: utf-8 -*-

from common.exceptions import *
from models import GameModel
from common.tools import add_user_things


class UserItems(GameModel):
    """ 玩家道具
    
    Attribute:
        items: 玩家所有道具信息dict, key为道具id, 
                value为此道具数量
                eg:
                {
                    'gachacoin_item': 1
                    'gachadiamond_item': 1
                }
    """
    def __init__(self, uid=''):
        self.uid = uid
        self.items = {}   # 所有 
    
    @classmethod
    def create(cls, uid):
        obj = cls(uid)
        obj.init()
        obj.put()
        return obj

    def init(self):
        """ 初始玩家卡牌
        """
        userInit_conf = self._userInit_config 
        init_items_conf = userInit_conf.get('init_items', {})
        self.items = init_items_conf
        self.put()
        

    def add_item(self, item_id, num=1):
        if num <= 0:
            raise ParamsErro
        if item_id in self.items:
            self.items[item_id] += num
        else:
            self.items[item_id] = num 
        self.put()
        return self.items[item_id]

    def del_item(self, item_id, num=1):
        if num <= 0 or item_id not in self.items or \
            self.items[item_id] < num:
            raise ParamsError
        self.items[item_id] -= num
        self.put()
        return self.items[item_id]

    def get_item_num(self, item_id):
        if item_id not in self.items:
            return 0
        return self.items[item_id]
