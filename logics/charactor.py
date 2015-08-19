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


def api_allot_nature(nature_type, num):
    """ api/charactor/allot_nature
    元素掌握度加点

    Args:
        natur_type(int): 元素类别
            蓝  0
            红  1
            绿  2
            褐  3
            黄  4
            紫  5
        num(int): 要加的点数
    """
    ubase = request.user
    tools.del_user_things(ubase, 'nature_remain', num) 
    tools.add_user_things(ubase, "nature_" + str(nature_type), num)
    return {}
        
