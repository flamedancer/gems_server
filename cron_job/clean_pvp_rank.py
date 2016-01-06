# -*- coding: utf-8 -*-

"""
    每天执行， 检查是否要清空pvp排行榜
crontab -e
0 0 * * * /usr/bin/python /home/guochen/gems_server/cron_job/clean_pvp_rank.py >> /home/guochen/gems_server/logs/gems.log 2>&1
"""

import datetime
import os
import sys
cur_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(cur_dir, ".."))
from common import rank
from common import game_config
from common.utils import total_isoweek




def clean():
    award_day = game_config.get_config_dir('common_config').get('pvp_award_weekday', 1)
    this_week = total_isoweek(start=award_day)
    # 此周为双周 且为发放奖励的日子
    td = datetime.datetime.today()
    is_award_day = this_week % 2 == 1 and td.isoweekday() == award_day 
    if is_award_day:
        # 清空
        pvp_rank = rank.get_pvp_rank.zremrangeallrank()
        print "********CronTab: reset pvp_rank success!", td

if __name__ == '__main__':
    clean()

