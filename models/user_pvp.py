#-*- coding: utf-8 -*-

from models import GameModel


class UserPvp(GameModel):
    """ 实时pvp 
    """ 
    def __init__(self, uid=''):
        # 玩家 属性数据
        self.uid = uid 
        self.all_star = 0 
        self.grade = 15 # 段位 
        self.light_star = 0     # 显示亮星个数 
        self.shade_star = 0  # 显示暗星个数 


