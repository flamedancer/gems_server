#-*- coding: utf-8 -*-

from models import GameModel


class UserModified(GameModel):
    """ 玩家基本属性
    """ 
    def __init__(self, uid=''):
        # 玩家 属性数据
        self.uid = uid 
        self.modified = {} 
    
