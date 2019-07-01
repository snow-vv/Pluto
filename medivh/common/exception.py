# -*- coding: UTF-8 -*-


class MedivhExceptionBase(Exception):
    code = 0
    message = ''

    def __init__(self, code=None, message=None):
        if code:
            self.code = code
        if message:
            self.message = message


class LoginRequireException(MedivhExceptionBase):
    code = 401
    message = '需要登录'


class PermissionDeniedException(MedivhExceptionBase):
    code = 403
    message = '没有权限'


class PasswordMismatchException(MedivhExceptionBase):
    code = 10000
    message = '用户名密码不匹配'


class RunInfoNotFountException(MedivhExceptionBase):
    code = 10001
    message = ""


class StatusMismactchException(MedivhExceptionBase):
    code = 10002
    message = "状态不正确"


class SlbException(MedivhExceptionBase):
    code = 10003
    message = "slb机器数不满足"


class GreyEcsNotOneException(MedivhExceptionBase):
    code = 10004
    message = "服务灰度机器数不为一"


class ExceedDingdingPostMsgLimitException(MedivhExceptionBase):
    code = 10005
    message = "超出钉钉机器人每分钟发送消息限制"


class NoCommitSHAException(MedivhExceptionBase):
    code = 10006
    message = "拉代码必须指定commit SHA"
