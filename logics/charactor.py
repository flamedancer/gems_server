#-*- coding: utf-8 -*-
""" 主角系统
"""

from bottle import request
from common.tools import *

def api_rename(new_name):
    """ api/charactor/rename
    重命名
    
    Args:
        new_name(str): 新的玩家名字
    """
    return {}


def api_allot_nature(type_num):
    """ api/charactor/allot_nature
    元素掌握度加点
            蓝  0
            红  1
            绿  2
            褐  3
            黄  4
            紫  5

    Args:
        type_num(dir): 元素类别-要加的数量
         例如：
            {
                0: 1,
                1: 4,
                3: 2,
                ....
            }
    """
    ubase = request.user
    need_remain_num = sum(type_num.keys())
    tools.del_user_things(ubase, 'nature_remain', need_remain_num) 
    for nature_type, num in type_num.items():
        tools.add_user_things(ubase, "nature_" + str(nature_type), num)
    return {}
        
