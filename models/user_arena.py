# -*- coding: utf-8 -*-

from common.exceptions import *
from models import GameModel
from common.tools import add_user_things


class UserArena(GameModel):
    """ 玩家竞技场
    
    Attribute:
        step:  竞技场状态 0未开启竞技  1选第一张卡 2选第二张卡...  5准备开始竞技 6完成竞技等待领取奖励 
        selected_cards: 玩家当前已近选择卡牌 
        cards_pool: 当前竞技场给的候选卡组
        total: 当前竞技场共打了几场
        win: 当前竞技场赢了几场,赢了10次或者输了2次这次竞技就不能再打了
        has_fight_uids: 玩家此次竞技打过的对手,不和重复的对手和自己打
    """
    def __init__(self, uid=''):
        self.uid = uid
        self.reset_arena()

    def reset_arena(self):
        self.step = 0 # 竞技场状态 0未开启竞技  1选第一张卡 2选第二张卡...  5准备开始竞技 6完成竞技等待领取奖励
        team_length = self._common_config['team_length']
        self.selected_cards = [''] * team_length
        self.cards_pool = []  # 每次新开启的竞技场随机给的卡组
        self.total = 0  # 此次竞技已打场数
        self.win = 0  # 此次竞技已赢场数
        self.has_fight_uids = [] # 已打过的uid
        self.put()

    def is_in_arena(self):
        return self.step != 0

    def can_fight(self):
        return self.step ==5 

    def pack_info(self):
        return {
            'step': self.step,
            'selected_cards': self.selected_cards,
            'cards_pool': self.cards_pool,
            'win': self.win,
            'lose': self.total - self.win,
        }
    
    def set_cards_pool(self, cards_pool):
        self.cards_pool = cards_pool
        self.put()

    def set_step(self, step):
        self.step = step
        self.put()

    def select_card(self, index, card_id):
        self.selected_cards[index] = card_id
        self.put()

    def inc_total(self):
        self.total += 1
        self.put()

    def inc_win(self):
        self.win += 1
        self.put()

    def add_fight_uid(self, uid):
        if uid:
            self.has_fight_uids.append(uid)
        self.put() 

