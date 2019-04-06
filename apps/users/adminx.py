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


class GlobalSettings(object):
    site_title = '后台管理系统'
    site_footer = '网站管理'
    menu_style = 'accordion'    # 标签折叠


# UserProfile的注册流程：
# 1、C:\Users\admin\Desktop\MxWeb\MxWeb\settings.py
#     AUTH_USER_MODEL = 'users.UserProfile'   获得用户数据模型
#
# 2、C:\Users\admin\Envs\mxonline_py36\Lib\site-packages\django\contrib\auth\__init__.py
#     def get_user_model  通过该方法django获得用户数据模型
#
# 3、C:\Users\admin\Desktop\MxWeb\extra_apps\xadmin\plugins\auth.py
#     User = get_user_model()
#     class UserAdmin(object):
#         change_user_password_template = None
#         list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
#         ...
#     site.register(User, UserAdmin)
#     Xadmin将用户数据模型注册


class EmailVerifyRecordAdmin(object):
    # pass
    list_display = ['code', 'email', 'send_type', 'send_time']
    search_fields = ['code', 'email', 'send_type']
    list_filter = ['code', 'email', 'send_type', 'send_time']
    # model_icon = 'fa fa-envelope'


class BannerAdmin(object):
    # pass
    list_display = ['title', 'image', 'url', 'index', 'add_time']
    search_fields = ['title', 'image', 'url', 'index']
    list_filter = ['title', 'image', 'url', 'index', 'add_time']


xadmin.site.register(EmailVerifyRecord, EmailVerifyRecordAdmin)
xadmin.site.register(Banner, BannerAdmin)
xadmin.site.register(views.BaseAdminView, BaseSetting)
xadmin.site.register(views.CommAdminView, GlobalSettings)
# xadmin.site.register(xadmin.views.BaseAdminView, BaseSetting)
