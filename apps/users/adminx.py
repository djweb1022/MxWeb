# -*- coding:utf-8 -*-
__author__ = 'yfj'
__date__ = '2018/10/25 12:55'

import xadmin
from xadmin import views

from .models import EmailVerifyRecord,Banner


class BaseSetting(object):
    # 开启主题功能
    enable_themes = True
    use_bootswatch = True


class EmailVerifyRecordAdmin(object):
    # pass
    list_display = ['code', 'email', 'send_type', 'send_time']
    search_fields = ['code', 'email', 'send_type']
    list_filter = ['code', 'email', 'send_type', 'send_time']


class BannerAdmin(object):
    # pass
    list_display = ['title', 'image', 'url', 'index', 'add_time']
    search_fields = ['title', 'image', 'url', 'index']
    list_filter = ['title', 'image', 'url', 'index', 'add_time']


xadmin.site.register(EmailVerifyRecord, EmailVerifyRecordAdmin)
xadmin.site.register(Banner, BannerAdmin)
xadmin.site.register(views.BaseAdminView, BaseSetting)
# xadmin.site.register(xadmin.views.BaseAdminView, BaseSetting)
