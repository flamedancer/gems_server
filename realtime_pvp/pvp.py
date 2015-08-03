# -*- coding: utf-8 -*-

import os
import sys
from json import dumps, loads
import random
import time
import datetime
import geventwebsocket
from geventwebsocket import WebSocketServer
from gevent.lock import Semaphore

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, base_dir)
import settings
from libs.dbs import app
from logics.login import get_user_info
from models.user_base import UserBase

port = "9040"

all_players = []  # 所有连接成功的玩家
all_players_lock = Semaphore()

INIT_BEAD_LIST = []
[INIT_BEAD_LIST.extend([i] * 40) for i in range(7)]
def _make_bead_list():
    """ 返回由200个0~6数字等概率组成的列表
    """        
    random.shuffle(INIT_BEAD_LIST)
    return INIT_BEAD_LIST[:200]

def add_player(player):
    all_players_lock.acquire()
    all_players.append(player)
    all_players_lock.release()

def del_player(player):
    all_players_lock.acquire()
    all_players.remove(player)
    all_players_lock.release()

def pier_clear(*uids):
    """玩家退出pvp的善后处
        清除 app.pier 中 uid 数据
    """
    for uid in uids:
        if uid in app.pier.get_data:
            app.pier.get_data.pop(uid)
    

def debug_print(*msgs):
    if settings.DEBUG:
       print(",".join(msgs))


def get_real_pvp_info(uid):
    pier_clear(uid)
    uBase = UserBase.create(uid) 
    uCards = uBase.user_cards 
    user_pvp_info = {
        'uid': uBase.uid,
        'name': uBase.name,
        'team': uCards.cur_team(),
    }
    return user_pvp_info



class Player(object):
    def __init__(self, core_id, websocket):
        self.core_id = core_id
        self.uid = ''

        self.opponent = None


        self.connecting = True

        self.fight_status = -2  # -2 为连接上未做任何操作  -1 readying等待合适对手中 0 找到对手，但可以取消  1 fighting正在pk  2 end战斗结束

        self.last_recv_fg = True    # 判断是否活跃通信的标示，用于主动断开长时间没有通信的玩家

        self.websocket = websocket

    def response_error(error_code, error_msg):
        msg = {
            'msgtype': msg_type,
            'timestamp': int(time.time()),
            'data': data or {},
            'errorcode': error_code,
            'errormsg': error_msg,
        }
        response = dumps(msg)
        self.websocket.send(response)

    def send(self, msg_type, data=None):
        """send msg to self
        """
        msg = {
            'msgtype': msg_type,
            'timestamp': int(time.time()),
            'data': data or {},
        }
        if self.connecting:
            response = dumps(msg)
            debug_print(">>>>>send-to: ", self.core_id, self.uid, response)
            self.websocket.send(response)

    def send_opponent(self, msg_type, data=None):
        if self.opponent:
            self.opponent.send(msg_type, data)

    def broad(self, msg_type, data=None):
        self.send(msg_type, data)
        self.send_opponent(msg_type, data)

    def say_log(self, *msg):
        print(''.join([str(datetime.datetime.now()), '@', self.uid, '|', self.core_id, ': ', str(msg)]))

    def handle_msg(self, msg):
        if msg is None:
            disconnect_player(self, reason='network-error')
            return
        msg = msg.strip()
        debug_print("<<<<<<reseve", self.core_id, self.uid, msg)
        try:
            msg_dict = loads(msg)
        except ValueError:
            print "!!!!!!erro json msg ", msg
            return
        check_msg = check_status(msg_dict)
        if check_msg:
            print "warnning: get logic_error_msg", msg_dict
            return
            self.response_error(msg_dict, check_msg)
        else:
            response_fuc = getattr(self, msg_dict['msgtype'], None)
            if not response_fuc:
                return
            #print 'ok!!!!!!', response
            self.last_recv_fg = True
            response_fuc(msg_dict['data'])

    def get_suitable_opponent(self):
        for player in all_players:
            if player is not self:
                return player

    def req_pvp(self, data):
        """<2> 1. client 发送pvp请求
        """
        self.uid = data['uid']
        self.send('rsp_pvp')
        self.say_log('I am reading to pvp.....')
        self.try_start_fight()

    def try_start_fight(self):
        """ 状态转为寻找对手中,尝试寻找合适对手 ,
            若找到,转向<3>1
        """
        self.say_log('I try to get a opponent......')
        opponent = self.get_suitable_opponent()
        self.fight_status = -1
        if opponent is None:
            return
        else:
            self.inf_readying_pvp(opponent)

    def inf_readying_pvp(self, opponent):
        """ <3>1 server匹配好一对对手后通知两边
        """
        self.opponent = opponent
        self.opponent.opponent = self
        self.say_log('I get oppoent ' + self.opponent.uid + '|', self.uid)
        self.broad('inf_readying_pvp')

    def ans_readying_pvp(self, data):
        """ <3>3 client 已经准备就绪
            状态改为准备战斗，不能主动取消
        """ 
        self.fight_status = 0
        self.inf_opponent_information()
    
    def inf_opponent_information(self):
        """ <3>4 提供对手信息
        """
        opp_info = get_real_pvp_info(self.opponent.uid)
        self.send('inf_opponent_information', opp_info)

    def ans_opponent_information(self, data):
        """ <3>5 client确认收到对手信息
            当两边都确认时,通知开始战斗
        """
        self.fight_status = 1
        if self.opponent.fight_status == 1:
            init_beads = data["init_beads"]
            attacker = random.choice([self.uid, self.opponent.uid])
            self.inf_start_fight(attacker=attacker, init_beads=init_beads) 

    def inf_start_fight(self, attacker, init_beads):
        """ <3>6 确认谁先手和珠盘通知两边开始战斗
        """
        data = {
            'attacker': attacker,
            'init_beads': init_beads,
            'sequence': _make_bead_list(),
        }
        self.broad('inf_start_fight', data)

    def ans_start_fight(self, data):
        """ <3>7
        """
        pass 

    def req_fight_command(self, data):
        """ <4>1、2、3 处理战斗数据对发
        """
        self.send('rsp_fight_command')
        self.send_opponent('inf_fight_command', data)

    def ans_fight_command(self):
        """ <4>4
        """
        pass

    def req_end_fight(self, data):
        """ <5>1、2 转态转为结束, 两边都结束时,
            给两边发结算数据
        """
        self.fight_status = 2
        self.send('rsp_end_fight')
        if self.opponent.fight_status == 2:
            winner = data["winner"]
            end_reason = data["end_reason"]
            self.inf_fight_result(winner, end_reason)

    def inf_fight_result(self, winner, end_reason):
        """ <5>3
        """
        loser = self.uid if winner != self.uid else self.opponent.uid   
        data = {
            'end_reason': end_reason,
            'winner': winner,
            'loser': loser,
        }         
        self.broad('inf_fight_result', data)

    def ans_fight_result(self):
        """ <5>5、5
        """
        self.connecting = False

    def req_cancel_pvp(self, data):
        """ 退出匹配或战斗主动投降
        """
        # 还未匹配上,回应后直接退出
        if self.fight_status < 0:
            self.send('rsp_cancel_pvp')
            disconnect_player(self, reason='cancel-matching')
            return
        # status0 为已匹配上玩家,忽略此操作
        elif self.fight_status == 0:
            return
        # status1 战斗中,视为投降
        elif self.fight_status == 1 and self.opponent:
            # 通知对方自己已经放弃
            self.send('rsp_cancel_pvp')
            disconnect_player(self, reason='cancel-fighting')
    
    def ans_cancel_pvp(self):
        pass

    def req_random_sequence(self, data):
        """ <7> 战斗中需要用来统一两边的随机数
        """
        if not self.fight_status == 1:
            return
        self.send('rsp_random_sequence')
        data = {
            "sequence": _make_bead_list(),
        }
        self.broad('inf_random_sequence', data)
    
    def ans_random_sequence(self, data):
        pass
        
        


def disconnect_player(player, reason=''):
    if not player.connecting and not player in all_players:
        return
    pier_clear(player.uid)

    player.connecting = False
    player.websocket.close()

    del_player(player)

    # 如果自己掉线或投降  判定对手胜利
    if player.fight_status == 1 and player.opponent and player.opponent.connecting:
        player.inf_fight_result(player.opponent.uid, reason)
        if reason.startswith('network-error'):
            print '\n 异常掉线了!!!!!  :****   ({}|--{})'.format(player.core_id, player.uid), datetime.datetime.now()

    print 'disconnect player:**** {}  ({}|--{})'.format(reason, player.core_id, player.uid)


def check_status(msg_data):
    if msg_data.get('errorcode'):
        print '!!Get a error, errormsg:', msg_data.get('errormsg', 'errormsg')
        return msg_data['errormsg']
    # check_keys = ['msgtype', 'coreid', 'datafield', 'msg_ref', 'rc', 'errormsg']
    check_keys = ['msgtype', 'timestamp', 'data']
    if set(check_keys) - set(msg_data.keys()):
        print '!!!!! json missing keys:', set(check_keys) - set(msg_data.keys())
        return 'missing keys'




def application(environ, start_response):
    websocket = environ.get("wsgi.websocket")
    if websocket is None:
        start_response('200 OK', [('Content-Type','text/html')])
        return ''
    core_id = environ['HTTP_SEC_WEBSOCKET_KEY']
    player = Player(core_id, websocket)
    add_player(player)
    print "\n##Connecting#########################websockets...", core_id, datetime.datetime.now()

    try:
        while player.connecting:
            message = websocket.receive()
            player.handle_msg(message)
    except geventwebsocket.WebSocketError, ex:
        print "{0}: {1}".format(ex.__class__.__name__, ex)
    finally:
        disconnect_player(player, reason='network-error')


def check_dead_user():
    """剔除长时间没有数据交互的晚间，每隔15秒检查
    """
    while True:
        # print "checking connecting"
        for user in all_players:
            # print user.uid
            if user.last_recv_fg == False:
                print "disconnect ", user.uid
                disconnect_player(user, reason='network-error:no-msg-in-15s')
            else:
                user.last_recv_fg = False
        time.sleep(15000)




if __name__ == "__main__":
    path = os.path.dirname(geventwebsocket.__file__)
    agent = "gevent-websocket/%s" % (geventwebsocket.get_version())

    # print "start check user connecting"         # 开启检查掉线玩家进程
    # thread.start_new_thread(check_dead_user, ())
    try:
        print "Running %s from %s" % (agent, path)
        print "start pvp serve", datetime.datetime.now()
        # 保证等待列表数据库表为空
        WebSocketServer(("", int(port)), application, debug=False).serve_forever()
    except KeyboardInterrupt:
        print "close-server"
