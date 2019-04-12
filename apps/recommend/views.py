from django.shortcuts import render
from datetime import datetime

from django.shortcuts import render
from django.views.generic import View
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.db.models import Q
from .models import UserRating, WatchingTime
from courses.models import Course, Lesson, Video


class InitialView(View):
    def get(self, request):
        return render(request, 'base.html', {})


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
