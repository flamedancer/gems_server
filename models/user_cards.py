# -*- coding: utf-8 -*-

from models import GameModel
from common.tools import add_user_things


class UserCards(GameModel):
    """ 玩家卡牌
    """
    def __init__(self, uid=''):
        self.uid = uid
        self.teams = []
        self.cards = {}
        self.init_team()

    def init_team(self):
        """ 玩家初始卡牌
        """
        init_team = self._userInit_config['init_team']
        for card_id in init_team:
            add_user_things(self, card_id, 1, 'init_team')
        team_len = self._common_config['team_length'] 
        init_team.extend([''] * (team_len - len(init_team)))
        self.teams.append(init_team)
        self.put()
        

    def add_card(self, card_id, num=1):
        if card_id in self.cards:
            self.cards[card_id]['num'] += num
        else:
            self.cards[card_id] = {
                'lv': 0,
                'favor': 0,
                'num': 1,
            }
        self.put()
        return self.cards[card_id]
