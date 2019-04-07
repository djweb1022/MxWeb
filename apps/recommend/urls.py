# -*- coding:utf-8 -*-
__author__ = 'yfj'
__date__ = '2019/4/6 10:21'


from django.conf.urls import url, include

from .views import InitialView, AddRating


urlpatterns = [
    # 课程列表页
    url(r'^initial/$', InitialView.as_view(), name='initial'),

    # 保存评分
    url(r'^add_rating/$', AddRating.as_view(), name='add_rating'),
]