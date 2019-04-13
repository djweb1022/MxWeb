from django.shortcuts import render
from datetime import datetime
import operator

from django.shortcuts import render
from django.views.generic import View
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.db.models import Q
from .models import UserRating, WatchingTime
from courses.models import Course, Lesson, Video
from utils.mixin_utils import LoginRequiredMixIn
import json


class InitialView(LoginRequiredMixIn, View):
    def get(self, request):
        # string_type = ''
        # string_tag = ''

        user = request.user

        # 对当前情境类别作判断，返回提示语
        def get_time_type(weekday_1, hour_1):
            string_type_1 = ''
            string_tag_1 = ''
            if 0 <= int(weekday_1) <= 4:
                if 6 <= int(hour_1) <= 11:
                    string_type_1 = '工作日上午'
                    string_tag_1 = '区间：周一至周五 每天6:00-11:59'
                elif 12 <= int(hour_1) <= 17:
                    string_type_1 = '工作日下午'
                    string_tag_1 = '区间：周一至周五 每天12:00-17:59'
                elif 18 <= int(hour_1) <= 23:
                    string_type_1 = '工作日晚间'
                    string_tag_1 = '区间：周一至周五 每天18:00-23:59'
                elif 0 <= int(hour_1) <= 5:
                    string_type_1 = '工作日凌晨'
                    string_tag_1 = '区间：周一至周五 每天0:00-5:59'
            elif 5 <= int(weekday_1) <= 6:
                if 6 <= int(hour_1) <= 11:
                    string_type_1 = '周末上午'
                    string_tag_1 = '区间：周六和周日 每天6:00-11:59'
                elif 12 <= int(hour_1) <= 17:
                    string_type_1 = '周末下午'
                    string_tag_1 = '区间：周六和周日 每天12:00-17:59'
                elif 18 <= int(hour_1) <= 23:
                    string_type_1 = '周末晚间'
                    string_tag_1 = '区间：周六和周日 每天18:00-23:59'
                elif 0 <= int(hour_1) <= 5:
                    string_type_1 = '周末凌晨'
                    string_tag_1 = '区间：周六和周日 每天0:00-5:59'
            else:
                string_type_1 = '无情境'
                string_tag_1 = '无区间'

            return string_type_1, string_tag_1

        get_time = datetime.now()
        hour = get_time.hour
        weekday = get_time.weekday()
        time_turple = get_time_type(weekday, hour)
        string_type = time_turple[0]
        string_tag = time_turple[1]

        # 下面统计观看时间最长的时间类型，作为该用户最喜欢的时间情境
        user_watchingtime = WatchingTime.objects.filter(user=request.user)
        list_timetype = []
        list_type_value = []
        # 获取所有已经出现的时间类型
        for record in user_watchingtime:
            list_timetype.append(record.time_type)
        # 去除重复值
        list_timetype = list(set(list_timetype))
        # 排序
        list_timetype = sorted(list_timetype)
        # 分类统计观看时长，返回字典
        for single_type in list_timetype:
            # print(single_type)
            user_type_watchingtime = WatchingTime.objects.filter(user=request.user, time_type=single_type)
            sum_time = 0
            for record_user_type_watchingtime in user_type_watchingtime:
                sum_time += record_user_type_watchingtime.time
            a = [single_type, sum_time]
            list_type_value.append(a)

        # 嵌套列表按字列表第二个值——时间总和 进行排序
        print(list_type_value)
        list_type_value = sorted(list_type_value, key=operator.itemgetter(1), reverse=True)
        print(list_type_value)
        # print(list_type_value[4][1])

        return render(request, 'recommend-initial.html', {
            'user': user,
            'string_type': string_type,
            'string_tag': string_tag,
        })


class Gettime(View):
    """返回当前时间、情境"""
    def post(self, request):
        get_time = datetime.now()
        year = get_time.year
        month = get_time.month
        day = get_time.day
        hour = get_time.hour
        minute = get_time.minute
        second = get_time.second

        # 若时、分、秒在0-9之间，前面加个0再显示
        def zeronum(num):
            if 0 <= int(num) <= 9:
                num = '0' + str(num)
            return num
        hour = zeronum(hour)
        minute = zeronum(minute)
        second = zeronum(second)

        string_now = '%d年%d月%d日 %s:%s:%s' % (year, month, day, hour, minute, second)

        data = {
            'string_now': string_now,
        }

        # return HttpResponse('{"status":"success"}', second)

        return HttpResponse(json.dumps(data), content_type='application/json')



class AddRating(View):
    """用户评分"""
    def post(self, request):
        rating_id = request.POST.get('rating_id', 0)
        rating_value = request.POST.get('rating_value', 0)

        course = Course.objects.get(id=int(rating_id))

        if not request.user.is_authenticated():
            # 判断用户登录状态
            return HttpResponse('{"status":"fail", "msg":"用户未登录"}', content_type='application/json')

        exist_records = UserRating.objects.filter(user=request.user, course=course)
        if exist_records:
            # 若用户已经对课程评过分，则删除已有评分
            exist_records.delete()

        user_rating = UserRating()
        if int(rating_id) > 0 and int(rating_value) > 0:
            user_rating.id_int_user = request.user.id
            user_rating.id_int_course = rating_id
            user_rating.user = request.user
            user_rating.course = course
            user_rating.rating = rating_value
            user_rating.save()
            return HttpResponse('{"status":"success", "msg":"已评分"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail", "msg":"评分出错"}', content_type='application/json')


class AddTime(View):
    """用户观看时长"""
    def post(self, request):
        """通过ajax获得前端传来的数据"""
        course_id = request.POST.get('course_id', 0)
        lesson_id = request.POST.get('lesson_id', 0)
        video_id = request.POST.get('video_id', 0)
        timevalue = request.POST.get('sTime', 0)

        """根据id进行实例化"""
        course = Course.objects.get(id=int(course_id))
        lesson = Lesson.objects.get(id=int(lesson_id))
        video = Video.objects.get(id=int(video_id))

        if int(course_id) > 0 and int(lesson_id) > 0 and int(video_id) > 0 and int(timevalue) >= 0:
            watchingtime = WatchingTime()
            watchingtime.id_int_user = request.user.id
            watchingtime.id_int_course = course_id
            watchingtime.id_int_lesson = lesson_id
            watchingtime.id_int_video = video_id
            watchingtime.user = request.user
            watchingtime.course = course
            watchingtime.lesson = lesson
            watchingtime.video = video
            watchingtime.time = timevalue

            # 获得目前的时间
            get_time = datetime.now()

            # 设定调试时间
            # get_time = datetime(2019, 3, 22, 18, 34, 55)

            # 保存时间为目前获得的时间，提取星期、小时的值
            watchingtime.add_time = get_time
            weekday = get_time.weekday()
            hour = get_time.hour

            # 对保存时间的类别作判断
            if 0 <= int(weekday) <= 4:
                if 6 <= int(hour) <= 11:
                    watchingtime.time_type = 1
                elif 12 <= int(hour) <= 17:
                    watchingtime.time_type = 2
                elif 18 <= int(hour) <= 23:
                    watchingtime.time_type = 3
                elif 0 <= int(hour) <= 5:
                    watchingtime.time_type = 4
            elif 5 <= int(weekday) <= 6:
                if 6 <= int(hour) <= 11:
                    watchingtime.time_type = 5
                elif 12 <= int(hour) <= 17:
                    watchingtime.time_type = 6
                elif 18 <= int(hour) <= 23:
                    watchingtime.time_type = 7
                elif 0 <= int(hour) <= 5:
                    watchingtime.time_type = 8
            else:
                watchingtime.time_type = 9

            # 指定保存时间为2019年3月22日12时34分55秒
            # watchingtime.add_time = datetime(2019, 3, 22, 12, 34, 55)

            watchingtime.save()
            return HttpResponse('{"status":"success", "value":"已保存"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail", "msg":"不保存"}', content_type='application/json')
