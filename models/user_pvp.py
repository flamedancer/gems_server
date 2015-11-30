#-*- coding: utf-8 -*-

import bisect
from models import GameModel


class UserPvp(GameModel):
    """ 实时pvp 
    """ 
    def __init__(self, uid=''):
        # 玩家 属性数据
        self.uid = uid 
        self.all_star = 0 
        self.grade = 0 # 段位 
        self.light_star = 0     # 显示亮星个数 
        self.shade_star = 0  # 显示暗星个数 
        self.consecutive_win = 0 # 连赢场数
        self.total_win = 0   #总胜场
        self.total_lose = 0  # 总负场

    @classmethod
    def create(cls, uid): 
        obj = cls(uid)
        obj.adjust()
        obj.put()
        return obj

    def team_info(self):
        uProperty = self.user_property
        uCards = self.user_cards
        team = uCards.cur_team()
        return {
            'nature_0': uProperty.nature_0,
            'nature_1': uProperty.nature_1,
            'nature_2': uProperty.nature_2,
            'nature_3': uProperty.nature_3,
            'nature_4': uProperty.nature_4,
            'nature_5': uProperty.nature_5,
            'team': team,
            'card_lv': [uCards.cards.get(cid, {'lv': 0})['lv'] for cid in team],
            'card_favor': [uCards.cards.get(cid, {'favor': 0})['favor'] for cid in team], 
        }

    def adjust(self):
        pvp_rank_stars = self._common_config['pvp_rank_stars']
        grade_index = bisect.bisect(pvp_rank_stars, self.all_star) - 1
        # 刚好到达最后一段满星, 前端显示全为亮星
        if self.all_star == pvp_rank_stars[-1]:
            self.light_star = self.all_star - pvp_rank_stars[grade_index - 1] 
        else:
            self.light_star = self.all_star - pvp_rank_stars[grade_index]
        if grade_index == len(pvp_rank_stars) - 1:
            self.shade_star = 0
        else:
            self.shade_star = pvp_rank_stars[grade_index + 1] - self.all_star
        self.grade = len(pvp_rank_stars) - grade_index
        # 如果超过最大星数,进入最强王者
        #if self.all_star > pvp_rank_stars[-1]:
        #    self.grade = 0
        
        
    def win(self):
        if self.consecutive_win >= 2 and self.grade > 5:
            self.all_star += 2
        else:
            self.all_star += 1
        self.consecutive_win += 1
        self.total_win += 1
        self.adjust()
        self.put()
    
    def lose(self):
        # 5段以下不减星
        if self.grade > 5:
            self.all_star = max(0, self.all_star - 1)
        self.consecutive_win = 0
        self.total_lose += 1
        self.adjust()
        self.put()

    def reset_pvp(self):
        pvp_rank_stars = self._common_config['pvp_rank_stars']
        if self.grade <= 5:
            self.all_star = pvp_rank_stars[5]
        else:
            self.all_satr = 0
        self.adjust()

