# -*- coding: utf-8 -*-

import bisect
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
        consecutive_win: 已连赢次数
        total_invade_win: 总侵略胜场
        total_invade_lose: 总侵略负场
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
        self.watch_team_index = ''
        self.refresh_cnt = 0
        self.consecutive_win = 0
        self.opponent = {}
        self.total_invade_win = 0
        self.total_defense_win = 0

    def set_opponent(self, opponent_info):
        self.opponent = opponent_info
        self.put()

    def watch_team_info(self):
        uProperty = self.user_property
        uCards = self.user_cards
        uCities = self.user_cities
        team = self.watch_team
        # 防守编队为空时，用当前编队
        if not team or set(team) == set(['']):
            team = uCards.cur_team() or self._common_config['init_team']
        team_index = self.watch_team_index or uCards.cur_team_index,
        return {
            'nature_0': uProperty.nature_0,
            'nature_1': uProperty.nature_1,
            'nature_2': uProperty.nature_2,
            'nature_3': uProperty.nature_3,
            'nature_4': uProperty.nature_4,
            'nature_5': uProperty.nature_5,
            'team': team,
            'team_index': team_index, 
            'team_index_lv': uCities.cities[team_index]['reputation_lv'],
            'card_lv': [uCards.cards.get(cid, {'lv': 0})['lv'] for cid in team],
            'card_favor': [uCards.cards.get(cid, {'favor': 0})['favor'] for cid in team],
            'city_lv': uCities.cities[uCities.capital_city or '0']['lv'],
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
            'team_index': uCards.cur_team_index,
            'team_index_lv': uCities.cities[team_index]['reputation_lv'],
            'card_lv': [uCards.cards.get(cid, {'lv': 0})['lv'] for cid in team],
            'card_favor': [uCards.cards.get(cid, {'favor': 0})['favor'] for cid in team],
        }

   
    def add_history(self, history_log):
        self.history.append(history_log)
        self.history = self.history[-20:]
        self.has_new_history = True
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
        invade_cup_rank = self._common_config['invade_cup_rank']
        self.cup_rank = len(invade_cup_rank) - bisect.bisect(invade_cup_rank, self.cup) + 1 
        self.put()
        return self.cup - old_cup

    def add_invade_jeton(self, num):
        self.invade_jeton = max(0, self.invade_jeton + num)
        self.put()

    def reset_shield_time(self, shield_time=0):
        self.shield_time = shield_time 

    def reset_refresh_cnt(self, new_time=0):
        self.refresh_cnt = new_time 

    def clear_opponent(self):
        self.opponent = {}
        self.put()

    def set_watch_team(self, index, team):
        """ 修改守城编队
        Args:
            team: 新的编队list
        """
        team_len = self._common_config['team_length']
        uCards = self.user_cards
        if len(team) != team_len:
            raise ParamsError('Team length error!')
        for card_id in team:
            if card_id == '':
                continue
            elif card_id not in uCards.cards:
                raise LogicError("Hasn't got card_id %s" % card_id)
            elif uCards.cards[card_id]['num'] <= 0:
                raise LogicError(" %s num is 0" % card_id)
            elif uCards.cards[card_id]['num'] < team.count(card_id):
                raise LogicError("%s num is not enough" % card_id)
        self.watch_team = team
        self.watch_team_index = index

    def inc_refresh_cnt(self):
        self.refresh_cnt += 1
        self.put()

    def reset_consecutive_win(self):
        self.consecutive_win = 0

    def inc_consecutive_win(self):
        self.consecutive_win += 1

    def inc_total_invade_win(self):
        self.total_invade_win += 1

    def inc_total_defense_win(self):
        self.total_defense_win += 1

    def reset_invade(self):
        """ 重置竞技场 """ 
        self.cup = 0
        invade_cup_rank = self._common_config['invade_cup_rank']
        self.cup_rank = len(invade_cup_rank)
        self.reset_shield_time()
        self.reset_refresh_cnt()
        self.clear_opponent()
        self.clear_history()
        self.reset_consecutive_win()

