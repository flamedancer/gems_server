# -*- coding: utf-8 -*-

from libs.model import TopModel

#统一管理排行版
RANKS = {}


def get_rank(top_name):
    # 获得指定排行榜   
    return RANKS.setdefault(top_name, TopModel.create(top_name))


def get_pvp_rank():
    return get_rank('realpvp')
