# -*- encoding: utf-8*

from models import GameModel
from common.exceptions import *

class UserCities(GameModel):
    """ 城市系统

    Attribute:
        captial_city: 主城id
        cities: 各城市信息dict, key为城市id, 不在此里的其它city
                为战争迷雾状态
            value 为城市dict:
                status:  0未开启  1开启  2已征服
                cur_conquer: 征服模式当前战场index
                lv    ： 等级
                team  :  城市卫队
                jeton :  该城市经费（城市代币）
                reputation: 声望值
                reputation_lv: 声望等级
    """
    def __init__(self, uid=''):
        self.uid = uid
        self.capital_city = '1'
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
        self.conquer_city('0')
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
            'lv': 1,
            'jeton': 0,
            'reputation': 0,
            'reputation_lv': 0,
            'team': [],
            'cur_conquer': 1,
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
        """ 开城
        """
        if not self.has_open_city(city_id):
            raise LogicError("Should open it first")
        self.cities[city_id]['status'] = 2
        self.put()
        return {city_id: {'status': 2}}

    def set_capital(self, city_id):
        if not has_conquer_city(city_id):
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

    def can_conquer_city(self, city_id):
        if self.has_open_city(city_id) and \
            self.cities[city_id]['status'] == 1:
            return True
        return False

    def get_opened_city_num(self):
        return len([city for city in self.cities if self.cities[city]['status'] >=1])

    def cur_conquer_stage(self, city_id):
        return str(self.cities[city_id]['cur_conquer'])

    def up_conquer_stage(self, city_id):
        self.cities[city_id]['cur_conquer'] += 1
        

