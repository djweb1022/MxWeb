# -*- coding:utf-8 -*-
__author__ = 'yfj'
__date__ = '2018/12/19 10:13'

from django.conf.urls import url, include
from .views import UserinfoView


urlpatterns = [
    # 课程列表页
    url(r'^info/$', UserinfoView.as_view(), name='user_info'),
    # 课程详情页
    # url(r'^detail/(?P<course_id>\d+)/$', CourseDetailView.as_view(), name='course_detail'),
]