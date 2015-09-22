# -*- coding: utf-8 -*-
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
        if weight_count <= random_weight:
            lucker = key
    return lucker
