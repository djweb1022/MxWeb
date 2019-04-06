# -*- coding:utf-8 -*-
__author__ = 'yfj'
__date__ = '2019/4/6 10:59'

import xadmin

from .models import UserRating


class UserRatingAdmin(object):
    list_display = ['user', 'course', 'rating', 'add_time']
    search_fields = ['user', 'course', 'rating']
    list_filter = ['user', 'course', 'rating', 'add_time']


xadmin.site.register(UserRating, UserRatingAdmin)
