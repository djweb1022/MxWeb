# -*- coding:utf-8 -*-
__author__ = 'yfj'
__date__ = '2018/12/19 10:13'

from django.conf.urls import url, include
from .views import UserinfoView, UploadImageView


urlpatterns = [
    # 课程列表页
    url(r'^info/$', UserinfoView.as_view(), name='user_info'),
    # 用户头像上传
    url(r'^image/upload/$', UploadImageView.as_view(), name='image_upload'),
]