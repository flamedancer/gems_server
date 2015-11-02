# -*- coding:utf-8 -*-
"""  pvp接口
"""

from bottle import request
from common import tools
from common.exceptions import *
from common import rank
from models.user_base import UserBase


def api_info():
    """ api/pvp/info
    pvp显示基本信息

    Retures:
        grade(int): 段位
        light_star: 显示亮星数
        shade_star: 显示暗星数
    """
    upvp = request.user.user_pvp
    return {
        'grade': upvp.grade,
        'light_star': upvp.light_star,
        'shade_star': upvp.shade_star,
    }


def api_top():
    """ api/pvp/top
    pvp排行榜
    
    Returns:
        tops(list): 排行榜个玩家信息
        self_rank(int): 自己排名,如为0代表未进入排行榜
        self_star(int): 自己星数
        star_gap(int): 距离上升需要星数
    """
    user = request.user
    tops = [] 

    #前5的排行情况
    top_model = rank.get_pvp_rank()
    top_uid_score = top_model.get(5)


    for uid, score in top_uid_score:
        base_obj = UserBase.get(uid)
        tops.append({
            'lv': base_obj.user_property.lv, 
            'name': base_obj.name, 
            'star': score,
        })

    self_rank = top_model.rank(user.uid)
    self_score = top_model.score(user.uid) or 0
    # 不在排行榜内 返回 0
    if self_rank is None:
        self_rank = 0
        star_gap = 0
    # top 的rank 第一名是 0
    else:
        star_gap = top_model.get_score(self_rank - 1) - self_score + 1
        self_rank += 1
    return {
        'tops': tops,
        'self_rank': self_rank,
        'star_gap': star_gap,
        'self_star': self_score,
    }

    
    
