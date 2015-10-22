#-*- coding: utf-8 -*-

import time
from models import GameModel
from common.exceptions import *


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
        self.dungeon = {}

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
                        self.modified['cities'][city_id] = info[city_id]
            else:
                self.modified['cities'] = info
        else:
            self.modified[thing] = info 
        self.put()

    def update_modify(self, new_info_dict):
        for item, info in new_info_dict.items():
            self.set_modify_info(item, info)
        self.put()
    
    def add_dungeon_info(self, dungeon_type, info=None): 
        if info is None:
            info = {}
        info['time'] = time.time()
        self.dungeon[dungeon_type] = info
        self.put()

    def clear_dungeon_info(self, dungeon_type):
        if dungeon_type not in self.dungeon:
            raise LogicError("End the wrong fight")
        info = self.dungeon.pop(dungeon_type)
        self.put()
        return info

    def has_dungeon_info(self, dungeon_type):
        return dungeon_type in self.dungeon  

    def get_dungeon_info(self, dungeon_type):
        """ 检查是否由此战场信息
        """
        if dungeon_type not in self.dungeon:
            raise LogicError("End the wrong fight")
        return self.dungeon[dungeon_type]
        
        
