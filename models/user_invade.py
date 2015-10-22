# -*- coding: utf-8 -*-

from common.exceptions import *
from models import GameModel
from common.tools import add_user_things


class UserInvade(GameModel):
    """ 玩家城战
    
    Attribute:
        cup: 获得奖杯数 
        cup_rank: 奖杯段位
        invade_jeton: 城战代币
        shield_time: 保护结束时间 
        watch_team: 防守阵容
        history: 防守日志
        has_new_history: 是否有新日志
        refresh_cnt: 已连续寻找对手次数
        opponent: 当前对手对手信息,可为空
            uid(str): 对手uid
            name(str): 对手名字
            lv(int): 多少等级
            expire_time(int): 此对手过期时间
            capitail_city(str): 对手主城id
            win_award(dict): 胜利获得奖励
            lose_award(dict)；失败获得奖励
    """
    def __init__(self, uid=''):
        self.uid = uid
        self.cup = 0
        invade_cup_rank = self._common_config['invade_cup_rank']
        self.cup_rank = len(invade_cup_rank)
        self.invade_jeton = 0
        self.shield_time = 0
        self.history = []
        self.has_new_history = False
        self.watch_team = []
        self.refresh_cnt = 0
        self.opponent = {}

    def set_opponent(self, opponent_info):
        self.opponent = opponent_info
        self.put()

    def watch_team_info(self):
        uProperty = self.user_property
        uCards = self.user_cards
        team = self.watch_team or uCards.cur_team()
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

    def now_team_info(self):
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

   
    def add_history(self, history_log):
        self.history.append(history_log)
        self.history = self.history[-20:]
        self.put()

    def clear_history(self, index=None):
        if index is not None:
            self.history.pop(index)
        else:
            self.history = []
        self.put()


    def add_cup(self, num):
        old_cup = self.cup
        self.cup = max(0, self.cup + num)
        self.put()
        return self.cup - old_cup

    def add_invade_jeton(self, num):
        self.invade_jeton = max(0, self.invade_jeton + num)
        self.put()

    def reset_shield_time(self):
        self.shield_time = 0
        self.put()

    def reset_refresh_cnt(self, new_time=0):
        self.refresh_cnt = new_time 
        self.put()

    def clear_opponent(self):
        self.opponent = {}
        self.put()

    def set_watch_team(self, new_team):
        """ 修改守城编队
        Args:
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
        self.watch_team = team
        self.put()
        