#-*- coding: utf-8 -*-
"""
    获取敌将编队
"""

from common.game_config import get_config_dir

def api_enemy():
    """ api/enemy/enemy
    
    获取敌将编队
    Returns:
        [
            "1_card",    #  卡片id
            3            #  开片level
        ],
        [
            "1_card",
            3
        ],
        [
            "1_card",
            3
        ],
        [
            "1_card",
            3
        ]
    """
    return get_config_dir('userInit_config').get('enemy_team', {})
    
