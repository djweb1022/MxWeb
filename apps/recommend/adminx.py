# -*- coding:utf-8 -*-
__author__ = 'yfj'
__date__ = '2019/4/6 10:59'

import xadmin

from .models import UserRating, WatchingTime


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


class WatchingTimeAdmin(object):
    list_display = ['id_int_user', 'id_int_course', 'user', 'course', 'time', 'add_time', 'timetype']
    search_fields = ['id_int_user', 'id_int_course', 'user', 'course', 'time']
    list_filter = ['id_int_user', 'id_int_course', 'user', 'course', 'time', 'add_time', 'timetype']

    def save_models(self):
        # 重载save_models，让用户和课程的整数型ID与外键ID始终保持一致
        obj = self.new_obj

        weekday = obj.add_time.weekday()
        year = obj.add_time.year
        month = obj.add_time.month
        day = obj.add_time.day
        hour = obj.add_time.hour
        minute = obj.add_time.minute
        second = obj.add_time.second
        microsecond = obj.add_time.microsecond

        obj.save()


xadmin.site.register(UserRating, UserRatingAdmin)
xadmin.site.register(WatchingTime, WatchingTimeAdmin)
