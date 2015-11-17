# -*- encoding: utf-8* import random
import bisect
import random
from models import GameModel
from common.exceptions import *

class UserCities(GameModel):
    """ 城市系统

    Attribute:
        captial_city(str): 主城id
        cities: 各城市信息dict, key为城市id(str), 不在此里的其它city
                为战争迷雾状态
            value 为城市dict:
                status(int):  0未开启  1开启  2已征服 3完成一轮挑战
                cur_conquer(int): 征服模式当前战场index
                lv(int)    :  等级
                team(int)  :  城市卫队
                jeton(int) :  该城市经费（城市代币）
                reputation(int): 声望值
                reputation_lv(int): 声望等级
                challenge(dict): 挑战模式各个大关卡对应的当前进行深度
    """
    def __init__(self, uid=''):
        self.uid = uid
        self.capital_city = ''
        self.city_award = {} 
        self.cities = {}

    @classmethod
    def create(cls, uid):
        obj = cls(uid)
        obj.init()
        obj.put()
        return obj

    def init(self):
        self.show_city('0')
        self.open_city('0')
        init_team = self._userInit_config['init_team']
        team_len = self._common_config['team_length']
        init_team.extend([''] * (team_len - len(init_team)))
        self.cities['0']['team'] = init_team
        self.put()

    def show_city(self, city_id):
        """ 打开战争迷雾
        """
        if city_id in self.cities:
            return {}
        self.cities[city_id] = {
            'status': 0,
            'lv': 0,
            'jeton': 0,
            'reputation': 0,
            'reputation_lv': 0,
            'team': [],
            'cur_conquer': 1,
            'challenge': {}
        }
        self.put()
        return {city_id: self.cities[city_id]}

    def open_city(self, city_id):
        """ 开城
        """
        if not self.has_show_city(city_id):
            raise LogicError("Should show it first")
        self.cities[city_id]['status'] = 1
        city_config = self._city_config
        modified = {}
        allies_cities = city_config[city_id]['allies']
        if allies_cities:
            for allies_city in allies_cities:
                new_city = self.show_city(allies_city)
                modified.update(new_city)
        self.put()
        modified[city_id] = {'status': 1}
        return modified

    def conquer_city(self, city_id):
        """ 征服城市
        """
        if not self.has_open_city(city_id):
            raise LogicError("Should open it first")
        self.cities[city_id]['status'] = 2
        self.up_city_lv(city_id)
        # 初始化挑战的关卡
        challenge_config = self._challenge_config
        for floor in challenge_config[city_id]:
            self.cities[city_id]['challenge'][floor] = 1
        self.put()
        return {city_id: {'status': 2,
                          'lv': self.cities[city_id]['lv'],
                          'challenge': self.cities[city_id]['challenge'],
                         }
        }

    def set_capital(self, city_id):
        if not self.has_conquer_city(city_id):
            raise "Cannot set this city capital"
        self.capital_city = city_id
        self.put()

    def has_show_city(self, city_id):
        if city_id in self.cities:
            return True
        return False

    def has_open_city(self, city_id):
        if self.has_show_city(city_id) and \
            self.cities[city_id]['status'] > 0:
            return True
        return False

    def has_conquer_city(self, city_id):
        if self.has_show_city(city_id) and \
            self.cities[city_id]['status'] > 1:
            return True
        return False

    def can_conquer_city(self, city_id):
        if self.has_open_city(city_id) and \
            self.cities[city_id]['status'] == 1:
            return True
        return False

    def can_challenge_city_floor(self, city_id, floor):
        if self.has_open_city(city_id) and \
            self.cities[city_id]['status'] >= 2 and \
            self.cities[city_id]['challenge'].get(floor, 6) < 6:
            return True
        return False

    def get_opened_city_num(self):
        return len([city for city in self.cities if self.cities[city]['status'] >=1])

    def get_conquered_city_num(self):
        return len([city for city in self.cities if self.cities[city]['status'] >=2])

    def cur_conquer_stage(self, city_id):
        return str(self.cities[city_id]['cur_conquer'])

    def up_conquer_stage(self, city_id):
        self.cities[city_id]['cur_conquer'] += 1
        self.put()
        return {city_id: {'cur_conquer': self.cities[city_id]['cur_conquer']}}

    def up_city_lv(self, city_id):
        max_city_lv = self._common_config['max_city_lv']
        self.cities[city_id]['lv'] = min(self.cities[city_id]['lv'] + 1, max_city_lv)
        self.put()

    def add_city_reputation(self, city_id, add_reputation):
        city_reputation_conf = self._common_config['city_reputation']
        new_rep = self.cities[city_id]['reputation'] + add_reputation
        self.cities[city_id]['reputation_lv'] = bisect.bisect(city_reputation_conf,
            new_rep) - 1
        self.cities[city_id]['reputation'] = min(max(city_reputation_conf), new_rep)
        return {city_id: {'reputation': self.cities[city_id]['reputation'],
                          'reputation_lv': self.cities[city_id]['reputation_lv'],
                         }
        }
        

    def up_challenge_stage(self, city_id, floor):
        self.cities[city_id]['challenge'][floor] += 1
        self.put()
        # 检查是否全部通关
        for room in self.cities[city_id]['challenge'].values():
            if room <= 5:
                break
        else:
            if self.cities[city_id]['status'] == 2:
                self.cities[city_id]['status'] = 3
                self.up_city_lv(city_id)
            self.refresh_challenge(city_id)
        return {city_id: {'challenge': self.cities[city_id]['challenge'],
                          'status': self.cities[city_id]['status'],
                          'lv': self.cities[city_id]['lv'],
                         }
        }


    def refresh_challenge(self, city_id):
        if not self.cities[city_id]['status'] >= 3:
            raise LogicError('Cannot refresh this city')
        city_challenge_conf = self._challenge_config[city_id]
        sample_city = random.sample(city_challenge_conf, 3)
        self.cities[city_id]['challenge'] = {city_id: 1 for city_id in sample_city}
        self.put()
        return {city_id: {'challenge': self.cities[city_id]['challenge']}}

    def add_city_jeton(self, city_id, num):
        self.cities[city_id]['jeton'] += num
        return {city_id: {'jeton': self.cities[city_id]['jeton']}}

    def set_city_award(self, award):
        self.city_award = award

