#-*- coding: utf-8 -*-


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class ParamsError(Error):
    """ 参数错误

    在游戏逻辑处理中发现前端传的参数有缺失
    或不符要求，抛出此异常
    """
    error_code = 6
    def __init__(self, error_msg):
        self.error_msg = error_msg


class TimeError(Error):
    """ 请求超时

    请求的时间戳和服务器时间相差过大
    """
    error_code = 1
    error_msg = u'请求超时'


class SignatureError(Error):
    """ 请求的参数签名错误
    
    每个游戏逻辑的请求都会有一个额外的参数,
    这个参数是根据其它几个参数加密后产生的,
    代表这次请求的合法性
       
    """
    error_code = 2
    error_msg = u'参数校验有误'


class AuthError(Error):
    """ 身份认证不通过
    
    根据Openid和Token进行身份认证 
    """
    error_code = 3
    error_msg = u"身份认证不通过"


class LogicError(Error):
    """ 严重游戏逻辑错误
    """
    error_code = 4
    error_msg = u"系统错误，请重进游戏！"

class LackError(Error):
    """ 行为条件未满足
    
    例如购买时金币不足等
    """   
    error_code = 5
    def __init__(self, error_msg):
        self.error_msg = error_msg


