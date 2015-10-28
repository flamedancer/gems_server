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
        self.grade = 15 # 段位 
        self.light_star = 0     # 显示亮星个数 
        self.shade_star = 5  # 显示暗星个数 
        self.consecutive_win = 0
        self.init()

    def init(self):
        pvp_rank_stars = self._common_config['pvp_rank_stars']
        self.grade = len(pvp_rank_stars)
        self.shade_star = pvp_rank_stars[0]
        self.put()

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
        self.light_star = self.all_star - pvp_rank_stars[grade_index]
        if grade_index == len(pvp_rank_stars) - 1:
            self.shade_star = 0
        else:
            self.shade_star = pvp_rank_stars[grade_index + 1] - self.all_stars
        self.grade = len(pvp_rank_stars) - self.grade_index 
        
        
    def win(self):
        if self.consecutive_win >= 2 and self.grade > 5:
            self.all_star += 2
        else:
            self.all_star += 1
        self.consecutiv_win += 1
        self.adjust()
        self.put()
    
    def lose(self):
        self.all_star = max(0, self.all_star - 1)
        self.consecutive_win = 0
        self.adjust()
        self.put()


