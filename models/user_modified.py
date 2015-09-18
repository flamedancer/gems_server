#-*- coding: utf-8 -*-

from models import GameModel


class UserModified(GameModel):
    """ 1.处理需通知前端及时更新的数据
        2.临时数据，例如保存进战场时的信息，
            以便出战场时的结算 
    """ 
    def __init__(self, uid=''):
        # 玩家 属性数据
        self.uid = uid 
        self.modified = {} 
        self.temp = {} 

    def set_modify_info(self, thing, info=None):
        if thing == 'cards':
            if 'cards' in self.modified:
                for card_id in info:
                    if card_id in self.modified['cards']:
                        self.modified['cards'][card_id].update(info[card_id])
                    else:
                        self.modified['cards'][card_id] = info[card_id]
            else:
                self.modified['cards'] = info
        elif thing == 'cities':
            if 'cities' in self.modified:
                for city_id in info:
                    if city_id in self.modified['cities']:
                        self.modified['cities'][city_id].update(info[city_id])
                    else:
                        self.modified['cards'][city_id] = info[city_id]
            else:
                self.modified['cities'] = info
        else:
            self.modified[thing] = info 
        self.put()
    
