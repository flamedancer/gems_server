# -*- coding: utf-8 -*-

import time
import random
from libs.model import BaseModel
from models.user_base import UserBase

class InvadeUser(BaseModel):
    """ 最近打过城战模式的玩家 
    """
    pk = 'invade'
    MAX_USER_NUM = 500
    invade = 1
    def __init__(self):
        self.users = {}

    @classmethod
    def get(cls):
        return super(InvadeUser, cls).get(cls.invade)

    @classmethod
    def get_instance(cls):
        obj = cls.get()
        if obj is None:
            obj = cls()
        obj.put() 
        return obj

    def add_user(self, uid, time_stamp=0):
        """
        Args:
            uid: 玩家id
            time: 保护时间 
        """
        self.users[uid] = time_stamp
        if len(self.users) >=self.MAX_USER_NUM:
            self.users.popitem()
        self.put()


    def get_fight_user(self, except_uids=None):
        """随机取得用户id
        """
        now = time.time()
        uids = [uid for uid in self.users if self.users[uid] < now] 
        uids = self.users.keys()
        if except_uids:
            uids = list(set(uids) - set(except_uids))
        if not uids:
            return self.make_virtual_user()
        selected_uid = random.choice(uids)
        selected_user = UserBase.get(selected_uid)
        selected_uproperty = selected_user.user_property
        selected_ucities = selected_user.user_cities
        return {
            'uid': selected_uid,
            'name': selected_user.name,
            'lv': selected_uproperty.lv,
            'capital_city': selected_ucities.capital_city,
        }

    def make_virtual_user(self):
        return {
            'uid': '',
            'name': 'test',
            'lv': 10,
            'capital_city': '0',
        }


