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

    def show_city(self, city_id):
        """ 打开战争迷雾
        """
        if city_id in self.cities:
            return
        self.cities[city_id] = {
            'status': 0, 
            'lv': 1,
            'jeton': 0,
            'reputation': 0,
            'reputation_lv': 0,
            'team': [],
            'cur_conquer': 1,
        }
            

    def open_city(self, city_id):
        """ 开城
        """
        if city_id not in self.cities:
            raise LogicError("Should show it first")
        self.cities[city_id]['status'] = 1
        city_config = self._city_config
        allies_cities = city_config[city_id]['allies'] 
        if allies_cities:
            for allies_city in allies_cities:
                self.show_city(allies_city)
    