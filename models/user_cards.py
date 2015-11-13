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
        self.cur_team_index = "0" # 当前使用城市卫队号
        self.cards = {}   # 所有 
        self.new_card_num = 0   # 新卡数量
    
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
        init_team = userInit_conf['init_team']
        init_cards_conf = userInit_conf.get('init_cards', {})
        for card_id in init_team:
            self.add_card(card_id, 1)
        for card_id,num in init_cards_conf.items(): 
            self.add_card(card_id, num)
        self.put()
        

    def add_card(self, card_id, num=1):
        if num <= 0:
            raise ParamsErro
        if card_id in self.cards:
            self.cards[card_id]['num'] += num
        else:
            self.cards[card_id] = {
                'lv': 1,
                'exp': 0,
                'favor': 0,
                'num': num,
                'is_new': True,
            }
            self.add_new_num()
        self.put()
        return self.cards[card_id]

    def del_card(self, card_id, num=1):
        if num <= 0 or not card_id in self.cards or \
            self.cards[card_id]['num'] < num:
            raise ParamsError
        self.cards[card_id]['num'] -= num
        self.put()
        return self.cards[card_id]

    def set_team(self, team_index, team):
        """ 修改编队
        Args:
            team_index: 要修改第几个城市编队
            team: 新的编队list
        """
        team_len = self._common_config['team_length'] 
        if len(team) != team_len:
            raise ParamsError('Team length error!')
        for card_id in team:
            if card_id == '':
                continue
            elif card_id not in self.cards:
                raise LogicError("Hasn't got card_id %s" % card_id)
            elif self.cards[card_id]['num'] <= 0:
                raise LogicError(" %s num is 0" % card_id)
            elif self.cards[card_id]['num'] < team.count(card_id):
                raise LogicError("%s num is not enough" % card_id)
        ucity = self.user_cities
        if not ucity.has_open_city(team_index): 
            raise LogicError("This city has't opened")
        ucity.cities[team_index]['team'] = team
        ucity.put()
        return team

    def set_cur_team_index(self, team_index):
        ucity = self.user_cities
        if not ucity.has_open_city(team_index): 
            raise LogicError("This city has't opened")
        self.cur_team_index = team_index
        self.put()

    def cur_team(self):
        ucity = self.user_cities
        return ucity.cities[self.cur_team_index]['team']

    def get_card_lv(self, card_id):
        if card_id == '':
            return 0
        if card_id not in self.cards:
            raise LogicError("Card not find")
        return self.cards[card_id]['lv']

    def add_card_lv(self, card_id, num):
        if card_id not in self.cards:
            raise LogicError("Card not find")
        self.cards[card_id]['lv'] += num
        self.put()
        return self.cards[card_id]

    def add_card_favor(self, card_id):
        if card_id not in self.cards:
            raise LogicError("Card not find")
        self.cards[card_id]['favor'] += 1
        self.put()
        return self.cards[card_id]

    def add_new_num(self, num=1):
        self.new_card_num = max(0, self.new_card_num + num)
        

