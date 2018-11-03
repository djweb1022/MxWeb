# -*- coding:utf-8 -*-
__author__ = 'yfj'
__date__ = '2018/11/3 14:59'

from django.conf.urls import url, include

from organization.views import OrgView, AddUserAskView

urlpatterns = [
    # 课程机构列表页
    url(r'^list/$', OrgView.as_view(), name='org_list'),
    url(r'^add_ask/$', AddUserAskView.as_view(), name='add_ask')
    # url(r'^home/(?P<prg_id>\d+)/$', AddUserAskView.as_view(), name='add_ask')
]