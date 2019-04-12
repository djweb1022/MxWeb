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
    list_display = ['id_int_user', 'id_int_course', 'user', 'course', 'time', 'add_time', 'time_type']
    search_fields = ['id_int_user', 'id_int_course', 'user', 'course', 'time']
    list_filter = ['id_int_user', 'id_int_course', 'user', 'course', 'time', 'add_time', 'time_type']

    def save_models(self):
        # 重载save_models，让用户和课程的整数型ID与外键ID始终保持一致
        obj = self.new_obj

        weekday = obj.add_time.weekday()
        # year = obj.add_time.year
        # month = obj.add_time.month
        # day = obj.add_time.day
        hour = obj.add_time.hour
        # minute = obj.add_time.minute
        # second = obj.add_time.second
        # microsecond = obj.add_time.microsecond

        if 0 <= int(weekday) <= 4:
            if 6 <= int(hour) <= 11:
                obj.time_type = 1
            elif 12 <= int(hour) <= 17:
                obj.time_type = 2
            elif 18 <= int(hour) <= 23:
                obj.time_type = 3
            elif 0 <= int(hour) <= 5:
                obj.time_type = 4
        elif 5 <= int(weekday) <= 6:
            if 6 <= int(hour) <= 11:
                obj.time_type = 5
            elif 12 <= int(hour) <= 17:
                obj.time_type = 6
            elif 18 <= int(hour) <= 23:
                obj.time_type = 7
            elif 0 <= int(hour) <= 5:
                obj.time_type = 8
        else:
            obj.time_type = 9

        obj.save()


xadmin.site.register(UserRating, UserRatingAdmin)
xadmin.site.register(WatchingTime, WatchingTimeAdmin)
