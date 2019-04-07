# -*- coding:utf-8 -*-
__author__ = 'yfj'
__date__ = '2019/4/6 10:59'

import xadmin

from .models import UserRating


class UserRatingAdmin(object):
    list_display = ['id_int_user', 'id_int_course', 'user', 'course', 'rating', 'add_time']
    search_fields = ['id_int_user', 'id_int_course', 'user', 'course', 'rating']
    list_filter = ['id_int_user', 'id_int_course', 'user', 'course', 'rating', 'add_time']

    def save_models(self):
        # 重载save_models，让用户和课程的整数型ID与外键ID始终保持一致
        obj = self.new_obj
        # obj.save()
        if obj.id_int_user != obj.user.id:
            obj.id_int_user = obj.user.id
        if obj.id_int_course != obj.course.id:
            obj.id_int_course = obj.course.id
        obj.save()


xadmin.site.register(UserRating, UserRatingAdmin)
