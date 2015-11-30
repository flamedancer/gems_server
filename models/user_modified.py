#-*- coding: utf-8 -*-

import time
from models import GameModel
from common.exceptions import *


class UserModified(GameModel):
    """ 1.处理需通知前端及时更新的数据
        2.临时数据，例如保存进战场时的信息，
            以便出战场时的结算 
        Attributs:
            guide_flags(dir): 根据value决定key功能的展示方式（0 正常显示, 1不提示但引导， 2提示且引导)
                arena  竞技场
                pvp    天梯
                invade 城战
                charactor 主角系统
                gacha   抽卡
                cards   图鉴系统
                task    任务
                challenge 挑战模式
                team_index_normal 获得新的军旗并进入除竞技场与城战防守外任意军旗界面-1默认转态
                team_index_special        玩家第一次获得新的军旗并进入竞技场军旗界面
    """ 
    def __init__(self, uid=''):
        # 玩家 属性数据
        self.uid = uid 
        self.modified = {} 
        self.temp = {} 
        self.guide_flags = {}   # 功能引导标记 
        self.dungeon = {}

    @classmethod
    def create(cls, uid):
        obj = cls(uid)
        obj.guide_flags = {
            'cards': 1,
            'task': 1,
            'team_index_normal': 0,
            'team_index_special': 0,
        }
        return obj


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

    def get_flags(self):
        """ 主页红点标志 """
        flags = [] 
        uproperty = self.user_property
        ucards = self.user_cards
        utask = self.user_task
        uinvade = self.user_invade
        uitems = self.user_items
        # 有剩余元素点
        if uproperty.nature_remain:
            flags.append("charactor") 
        # 有新卡 
        if ucards.new_card_num:
            flags.append("cards") 
        # 有已完成或新任务
        if utask.has_new_task:
            flags.append("task") 
        # 有新的防守日志
        if uinvade.has_new_history:
            flags.append("invade")    
        # 可以抽卡 
        if uitems.get_item_num("gachadiamond_item") or uitems.get_item_num("gachacoin_item"):
            flags.append("gacha")    
        return flags
    
    def has_guide_flags(self, flag):
        return flag in self.guide_flags

    def set_guide_flags(self, flag, sign):
        self.guide_flags[flag] = sign

    def del_guide_flags(self, flag):
        if flag in self.guide_flags:
            self.guide_flags.pop(flag)
        
