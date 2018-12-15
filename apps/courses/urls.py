# -*- coding:utf-8 -*-
__author__ = 'yfj'
__date__ = '2018/11/5 10:26'

from django.conf.urls import url, include
from courses.views import CourseListView, CourseDetailView, CourseInfoView


urlpatterns = [
    # 课程列表页
    url(r'^list/$', CourseListView.as_view(), name='course_list'),
    # 课程详情页
    url(r'^detail/(?P<course_id>\d+)/$', CourseDetailView.as_view(), name='course_detail'),

    url(r'^info/(?P<course_id>\d+)/$', CourseInfoView.as_view(), name='course_info'),
]