# -*- coding:utf-8 -*-
__author__ = 'yfj'
__date__ = '2018/10/25 12:55'

import xadmin

from .models import EmailVerifyRecord


class EmailVerifyRecordAdmin(object):
    pass


xadmin.site.register(EmailVerifyRecord, EmailVerifyRecordAdmin)