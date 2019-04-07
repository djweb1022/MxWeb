# -*- coding:utf-8 -*-
__author__ = 'yfj'
__date__ = '2019/4/6 10:59'

import xadmin

from .models import UserRating


class UserRatingAdmin(object):
    list_display = ['id_int_user', 'id_int_course', 'user', 'course', 'rating', 'add_time']
    search_fields = ['id_int_user', 'id_int_course', 'user', 'course', 'rating']
    list_filter = ['id_int_user', 'id_int_course', 'user', 'course', 'rating', 'add_time']


xadmin.site.register(UserRating, UserRatingAdmin)
