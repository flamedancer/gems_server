# -*- coding: utf-8 -*-

import random
from libs.model import BaseModel
from models.user_base import UserBase

class ArenaUser(BaseModel):
    """ 最近打过竞技模式的玩家 
    """
    pk = 'arena'
    MAX_USER_NUM = 1000
    arena = 1
    def __init__(self):
        """ 初始化当前排名数据
        """
        self.users = {}

    @classmethod
    def get(cls):
        return super(ArenaUser, cls).get(cls.arena)

    @classmethod
    def get_instance(cls):
        obj = cls.get()
        if obj is None:
            obj = cls()
        obj.put() 
        return obj

    def add_user(self, uid, team):
        """
        Args:
            uid: 玩家id
            team: 竞技场编队
        """
        self.users[uid] = team
        if len(self.users) >=self.MAX_USER_NUM:
            self.users.popitem()
        self.put()


    def get_random_user(self, except_uids=None):
        """随机取得用户id,和竞技场基本信息
        """
        uids = self.users.keys()
        if except_uids:
            for uid in except_uids:
                if uid in uids:
                    uids.remove(uid)
        if not uids:
            return self.make_virtual_user()
        selected_uid = random.choice(uids)
        selected_user = UserBase.get(selected_uid)
        selected_property = selected_user.user_property
        return {
            'uid': selected_uid,
            'name': selected_user.name,
            'lv': selected_property.lv,
            'nature_0': selected_property.nature_0,
            'nature_1': selected_property.nature_1,
            'nature_2': selected_property.nature_2,
            'nature_3': selected_property.nature_3,
            'nature_4': selected_property.nature_4,
            'nature_5': selected_property.nature_5,
            'team': self.uids[selected_uid],
        }

    def make_virtual_user(self):
        return {
            'uid': '',
            'name': 'test',
            'lv': 10,
            'nature_0': 10,
            'nature_1': 10,
            'nature_2': 10,
            'nature_3': 10,
            'nature_4': 10,
            'nature_5': 10,
            'team': ['1_card', '2_card', '3_card', '4_card'], 
        }


