# -*- coding:utf-8 -*-
__author__ = 'yfj'
__date__ = '2019/4/6 10:21'


from django.conf.urls import url, include

from .views import InitialView


urlpatterns = [
    # 课程列表页
    url(r'^initial/$', InitialView.as_view(), name='initial'),
]