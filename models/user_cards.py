# -*- coding: utf-8 -*-

from common.exceptions import *
from models import GameModel
from common.tools import add_user_things


class UserCards(GameModel):
    """ 玩家卡牌
    
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
        self.teams = []   # 编队序列
        self.cur_team_index = 0 # 当前使用编队序号
        self.cards = {}   # 所有 
    
    @classmethod
    def create(cls, uid):
        obj = cls(uid)
        obj.init_team()
        obj.put()
        return obj

    def init_team(self):
        """ 初始玩家卡牌
        """
        init_team = self._userInit_config['init_team']
        for card_id in init_team:
            self.add_card(card_id, 1)
        team_len = self._common_config['team_length'] 
        init_team.extend([''] * (team_len - len(init_team)))
        self.teams.append(init_team)
        team_number = self._common_config['team_number']
        self.teams.extend([[]] * (team_number - 1))
        self.put()
        

    def add_card(self, card_id, num=1):
        if num <= 0:
            raise ParamsErro
        if card_id in self.cards:
            self.cards[card_id]['num'] += num
        else:
            self.cards[card_id] = {
                'lv': 0,
                'exp': 0,
                'favor': 0,
                'num': num,
            }
        self.put()
        return self.cards[card_id]

    def del_card(self, card_id, num=1):
        if num <= 0 or not card_id in self.cards or \
            self.cards[card_id]['num'] < num:
            raise ParamsErro
        self.cards[card_id]['num'] -= num
        self.put()
        return self.cards[card_id]

    def set_team(self, team_index, team):
        """ 修改编队
        Args:
            team_index: 要修改第几个编队
            team: 新的编队list
        """
        team_len = self._common_config['team_length'] 
        if len(team) != team_len:
            raise ParamsError('Team length error!')
        if set(team) == set(['']):
            raise ParmasError('Can\'t set empty team !')
        for card_id in team:
            if card_id == '':
                continue
            elif card_id not in self.cards:
                raise LogicError("Hasn't got card_id %s" % card_id)
            elif self.cards[card_id]['num'] <= 0:
                raise LogicError("Cards: %s num is 0" % card_id)
                
        self.teams[team_index] = team
        self.put()
        return self.teams

    def set_cur_team_index(self, team_index):
        if not (0<= team_index < len(self.teams)):
            raise LogicError("No this index") 
        self.put()
        self.cur_team_index = team_index

    def cur_team(self):
        return self.teams[self.cur_team_index]

    def add_card_lv(self, card_id, num):
        if card_id not in self.cards:
            raise LogicError("Card not find")
        self.cards[card_id]['lv'] += num
        self.put()
        
