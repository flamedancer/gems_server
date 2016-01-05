# -*- coding: utf-8 -*-

import os
import sys
from json import dumps, loads
import random
import time
import datetime
import gevent
import geventwebsocket
from geventwebsocket import WebSocketServer
#from gevent.lock import Semaphore

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, base_dir)
import settings
from libs.dbs import app
from logics.login import get_user_info
from models.user_base import UserBase
from models.user_pvp import UserPvp
from models.user_property import UserProperty
from common import rank
from common import tools
from common.utils import print_err

port = "9081" if len(sys.argv) != 2 else sys.argv[1]

all_players = []  # 所有连接成功的玩家

pear_dict = {}  # 配对信息

INIT_BEAD_LIST = []
[INIT_BEAD_LIST.extend([i] * 40) for i in range(7)]

talkers = []

def _make_bead_list():
    """ 返回由200个0~6数字等概率组成的列表
    """        
    random.shuffle(INIT_BEAD_LIST)
    return INIT_BEAD_LIST[:200]

def add_all_player(player):
    all_players.append(player)

def del_all_player(player):
   if player not in all_players:
       return 
   all_players.remove(player)

def add_pear_dict(player):
    pear_dict[player.uid] = player.opponent

def del_pear_dict(player):
    if not player or player.uid not in pear_dict:
        return
    pear_dict.pop(player.uid, None)

def pier_clear(*uids):
    """玩家退出pvp的善后处
        清除 app.pier 中 uid 数据
    """
    for uid in uids:
        if uid in app.pier.get_data:
            app.pier.get_data.pop(uid)
        if uid in app.pier.put_data:
            app.pier.put_data.pop(uid)

def debug_print(*msgs):
    if settings.DEBUG:
       print(",".join(msgs))

def get_real_pvp_info(uid):
    pier_clear(uid)
    uBase = UserBase.create(uid) 
    uProperty = uBase.user_property
    uCards = uBase.user_cards 
    uCities = uBase.user_cities 
    team = uCards.cur_team()
    user_pvp_info = {
        'uid': uBase.uid,
        'lv': uProperty.lv,
        'name': uBase.name,
        'team': team,
        'team_index': uCards.cur_team_index,
        'team_index_lv': uCities.cities[uCards.cur_team_index]['reputation_lv'],
        'capital': uCities.capital_city,
        'nature_0': uProperty.nature_0,
        'nature_1': uProperty.nature_1,
        'nature_2': uProperty.nature_2,
        'nature_3': uProperty.nature_3,
        'nature_4': uProperty.nature_4,
        'nature_5': uProperty.nature_5,
        'card_lv': [uCards.cards.get(cid, {'lv': 0})['lv'] for cid in team],
        'card_favor': [uCards.cards.get(cid, {'favor': 0})['favor'] for cid in team],
    }
    pier_clear(uid)
    return user_pvp_info


class Player(object):
    def __init__(self, core_id, websocket):
        self.core_id = core_id
        self.uid = ''

        self.opponent = None

        self.connecting = True

        # -3 为连接上未做任何操作  -2 readying等待合适对手中 -1 找到对手，但可以取消
        # 0准备战斗中(找到对手，但不可以可以取消) 1 fighting正在pk  2 end战斗结束
        self.fight_status = -3 

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
            print '\n   意外断线！  :****   ({}|--{})'.format(self.core_id, self.uid), datetime.datetime.now()
            disconnect_player(self, reason='network-error: msg is None')
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
            if player.uid and player.uid != self.uid and player.fight_status == -2:
                return player

    def req_pvp(self, data):
        """<2> 1. client 发送pvp请求
        """
        self.uid = data['uid']
        # 判断体力是否足够
        uproperty = UserProperty.get(self.uid) 
        need_stamina = uproperty._common_config['pvp_stamina'] 
        if uproperty.stamina < need_stamina:
            print '\n   体力不足！  :****   ({}|--{})'.format(self.core_id, self.uid), datetime.datetime.now()
            disconnect_player(self, reason='Lack of stamina')
            

        self.send('rsp_pvp')
        self.say_log('I am reading to pvp.....')
        self.try_start_fight()

    def try_start_fight(self):
        """ 状态转为寻找对手中,尝试寻找合适对手 ,
            若找到,转向<3>1
        """
        self.say_log('I try to get a opponent......')
        opponent = self.get_suitable_opponent()
        if opponent is None:
            self.fight_status = -2
            return
        else:
            self.inf_readying_pvp(opponent)

    def inf_readying_pvp(self, opponent):
        """ <3>1 server匹配好一对对手后通知两边
        """
        self.fight_status = -1
        opponent.fight_status = -1
        self.opponent = opponent
        self.opponent.opponent = self

        add_pear_dict(self)
        add_pear_dict(opponent)
        self.say_log('I get oppoent ' + self.opponent.uid + '|', self.uid)
        self.broad('inf_readying_pvp')

    def ans_readying_pvp(self, data):
        """ <3>3 client 已经准备就绪
            当收到两边都准备好后
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

    def ans_fight_command(self, data):
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
            end_reason = data.get("end_reason", "normal")
            self.inf_fight_result(winner, end_reason)

    def inf_fight_result(self, winner, end_reason):
        """ <5>3
        """
        loser = self.uid if winner != self.uid else self.opponent.uid   
        # 玩家加星
        upvp_win = UserPvp.get(winner) 
        upvp_lose = UserPvp.get(loser) 
        full_exp = upvp_win._common_config['pvp_exp']
        upvp_win.win()
        tools.add_user_things(upvp_win, 'exp', full_exp, 'pvp_end')
        upvp_lose.lose()
        tools.add_user_things(upvp_lose, 'exp', int(full_exp / 3), 'pvp_end')
        upvp_win.do_put()
        upvp_lose.do_put()
        print "   Fight has end by reason: {}".format(end_reason)
        print "    WINNER : {}  || LOSER : {}".format(winner, loser)
        # 更新排行榜
        top_model = rank.get_pvp_rank()
        top_model.set(winner, upvp_win.all_star)
        top_model.set(loser, upvp_lose.all_star)
        pier_clear(loser, winner)
        data = {
            'end_reason': end_reason,
            'winner': winner,
            'loser': loser,
        }         
        self.broad('inf_fight_result', data)

    def ans_fight_result(self, data):
        """ <5>5、5
        """
        disconnect_player(self, reason='end-pvp')
        # self.connecting = False

    def req_cancel_pvp(self, data):
        """ 退出匹配或战斗主动投降
        """
        # 还未匹配上,回应后直接退出
        if self.fight_status < -1:
            self.send('rsp_cancel_pvp')
            print '\n   取消匹配！  :****   ({}|--{})'.format(self.core_id, self.uid), datetime.datetime.now()
            disconnect_player(self, reason='cancel-matching')
            return
        # status0 为已匹配上玩家,忽略此操作
        elif self.fight_status == 0:
            return
        # status1 战斗中,视为投降
        elif self.fight_status == 1 and self.opponent:
            # 通知对方自己已经放弃
            self.send('rsp_cancel_pvp')
            print '\n   主动投降！  :****   ({}|--{})'.format(self.core_id, self.uid), datetime.datetime.now()
            # 将自己和对方标记为已结算状态，防止多次投降结算
            self.fight_status = 2
            self.opponent.fight_status = 2
            self.inf_fight_result(self.opponent.uid, end_reason='cancel-fighting')
    
    def ans_cancel_pvp(self, data):
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

    def req_random_num(self, data):
        min_num = data['min']
        max_num = data['max']
        random_num = random.randint(min_num, max_num)
        self.send('rsp_random_num')
        data = {
            'random_num': random_num,
        }
        self.braod('inf_random_num', data)

    def ans_random_num(self, data):
        pass


def disconnect_player(player, reason='', force=False):
    if not force and not player.connecting:
        return
    # 禁用 send
    player.connecting = False 
    # 已结算战斗 
    if reason == 'end-pvp':
        clear_player(player)
    # 非正常退出(掉线、超时等)  且在战斗中 判定对手胜利
    elif player.fight_status in [0, 1] and player.opponent and player.opponent.connecting:
        #if reason.startswith('network-error'):
        #    print '\n 战斗中掉线!!判负  :****   ({}|--{})'.format(player.core_id, player.uid), datetime.datetime.now()
        player.inf_fight_result(player.opponent.uid, reason)
        clear_player(player)
    else:
        clear_player(player)
    print 'disconnect player:**** {}  ({}|--{})'.format(reason, player.core_id, player.uid)


def clear_player(player):
    del_all_player(player)
    del_pear_dict(player.opponent)
    # 已近进入战斗要扣体力
    if player.fight_status >= 1:
        uproperty = UserProperty.get(player.uid) 
        need_stamina = uproperty._common_config['pvp_stamina'] 
        tools.del_user_things(uproperty, 'stamina', need_stamina, 'pvp_start')
        uproperty.do_put()
    pier_clear(player.uid)

    player.connecting = False
    if not player.websocket.closed:
        player.websocket.close()



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
    print "\n##Connecting#########################websockets...", core_id, datetime.datetime.now()
    if environ['PATH_INFO'] == '/chat/':
        talkers.append(websocket)
        while 1:
            message = websocekt.receive()
            if message is None:
                break
            closed = []
            for talker in talkers:
                if talker.closed:
                    closed.append(closed)
                continue
                websocket.send(message)
            for dead_talker in closed:
                talkers.remove(talker)
        if websocket in talker:
            talkers.remove(websocekt)
    
    else:
        player = Player(core_id, websocket)
        add_all_player(player)

        try:
            while player.connecting:
                message = websocket.receive()
                player.handle_msg(message)
        except geventwebsocket.WebSocketError as ex:
            print "{0}: {1}".format(ex.__class__.__name__, ex)
        except Exception as ex:
            print_err()
            raise ex
        finally:
            disconnect_player(player, reason='Give up connecting finally')


def check_dead_user():
    """剔除长时间没有数据交互的晚间，每隔15秒检查
    """
    while True:
        gevent.sleep(600)
        if not all_players:
            continue
        print '='*20,"SSSSSSstart_check dead_user at", datetime.datetime.now()
        remove_players = []
        # print "checking connecting"
        for user in all_players:
            # print user.uid
            if user.last_recv_fg == False:
                remove_players.append(user)
            else:
                user.last_recv_fg = False
        for user in remove_players:
            print "disconnect ", user.uid, user.core_id
            disconnect_player(user, reason='Too long time no-msg-in-or-out', force=True)
            print "now the connecting user counter is", len(all_players) 
        print '='*10,"EEEEEnd_check dead_user at", datetime.datetime.now()


if __name__ == "__main__":
    path = os.path.dirname(geventwebsocket.__file__)
    agent = "gevent-websocket/%s" % (geventwebsocket.get_version())
    print "start check user connecting"         # 开启检查掉线玩家进程
    gevent.spawn(check_dead_user).start()

    try:
        print "Running %s from %s" % (agent, path)
        print "start pvp serve", datetime.datetime.now()
        # 保证等待列表数据库表为空
        WebSocketServer(("", int(port)), application, debug=False).serve_forever()
    except KeyboardInterrupt:
        print "close-server"

