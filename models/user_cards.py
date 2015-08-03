# -*- coding: utf-8 -*-

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
        obj = UserCards(uid)
        obj.init_team()
        obj.put()
        return obj

    def init_team(self):
        """ 初始玩家卡牌
        """
        init_team = self._userInit_config['init_team']
        for card_id in init_team:
            add_user_things(self, card_id, 1, 'init_team')
        team_len = self._common_config['team_length'] 
        init_team.extend([''] * (team_len - len(init_team)))
        self.teams.append(init_team)
        team_number = self._common_config['team_number']
        self.teams.extend([[]] * (team_number - 1))
        self.put()
        

    def add_card(self, card_id, num=1):
        if card_id in self.cards:
            self.cards[card_id]['num'] += num
        else:
            self.cards[card_id] = {
                'lv': 0,
                'exp': 0,
                'favor': 0,
                'num': 1,
            }
        self.put()
        return self.cards[card_id]

    def organize_team(self, team_index, team):
        """ 修改编队
        Args:
            team_index: 要修改第几个编队
            team: 新的编队list
        """
        self.teams[team_index] = team
        self.put()

    def cur_team(self):
        return self.teams[self.cur_team_index]

