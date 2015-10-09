# -*- coding: utf-8 -*-

from common.exceptions import *
from models import GameModel
from common.tools import add_user_things


class UserArena(GameModel):
    """ 玩家竞技场
    
    Attribute:
        team: 玩家编队list, len为common_config['team_number'] 每个玩家总共可以编队数,
              其中每个item为一个编队, card_id组成的list,''代表这个位置没有武将,len为common_config['team_length'],
             eg:
                [['1_card', '', '2_card', '3_card', ''],[],[],[],[]]
        cards: 玩家所有武将信息dict, key为武将id, 
                value为武将数据dict:
                    lv  武将等级
                    exp  武将经验
                    favor 武将好感度
                    num 有多少个此武将
                eg:
                {
                    '1_card':{
                        'lv': 0,
                        'exp':0,
                        'favor:0,
                        'num':1,
                    }
                }
    """
    def __init__(self, uid=''):
        self.uid = uid
        self.step = 0 # 竞技场状态 0未开启竞技  1选第一张卡 2选第二张卡...  5准备开始竞技 6完成竞技等待领取奖励
        team_length = self._common_config['team_length']
        self.selected_cards = [''] * team_length
        self.cards_pool = []  # 每次新开启的竞技场随机给的卡组
        self.total = 0  # 此次竞技已打场数
        self.win = 0  # 此次竞技已赢场数
        self.has_fight_uids = [] # 已打过的uid

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

