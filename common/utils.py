# -*- coding: utf-8 -*-
import sys
import  traceback
import time
import random


def get_key_by_weight_dict(item_weight_dict):
    """ 从 key - weight 的dict中按 权重weight选取key
        例如 {
                "1": 2,
                "2", 6,
                "3", 4,
                "4", 8, 
             }
        取得1，2，3，4，的概率分别为 0.1，0.3， 0.2， 0.4
    """
    all_weight = sum(item_weight_dict.values())
    random_weight = random.randint(1, all_weight)

    weight_count = 0
    lucker = None
    for key, value in item_weight_dict.items():
        weight_count += value
        if weight_count >= random_weight:
            lucker = key
            break
    return lucker


def total_isoweek(stamp=None, start=1):
    """ 今天是北京时间1970年01月01日(周四)08时00分00秒起第几周
    以周start为一周开始，初始为第0周
    """
    if start >= 4:
        indentday = start - 4
    else:
        indentday = 7 + start - 4
    if stamp is None:
        stamp = time.time()
    return int((stamp + 86400 * indentday) / (86400 * 7))


def print_err():
    sys.stderr.write('=='*30+os.linesep)
    sys.stderr.write('err time: '+str(datetime.datetime.now())+os.linesep)
    sys.stderr.write('--'*30+os.linesep)
    traceback.print_exc(file=sys.stderr)
    sys.stderr.write('=='*30+os.linesep)
