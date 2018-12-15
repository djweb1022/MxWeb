# -*- coding:utf-8 -*-
from django.shortcuts import render
from django.views.generic import View
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse

from .models import Course
from operation.models import UserFavorite

# Create your views here.


class CourseListView(View):
    def get(self, request):
        all_courses = Course.objects.all().order_by('-add_time')

        hot_courses = Course.objects.all().order_by('-click_nums')[:3]

        # 课程排序
        sort = request.GET.get('sort', '')
        if sort:
            if sort == 'students':
                all_courses = all_courses.order_by('-students')
            elif sort == 'hot':
                all_courses = all_courses.order_by('-click_nums')

        # 对课程进行分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_courses, 6, request=request)
        courses = p.page(page)

        return render(request, 'course-list.html', {
            'all_courses': courses,
            'sort': sort,
            'hot_courses': hot_courses,
        })


class CourseDetailView(View):
    """课程详情页"""
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        # 增加课程点击数
        course.click_nums += 1
        course.save()

        has_fav_course = False
        has_fav_org = False

        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=int(course.id), fav_type=1):
                has_fav_course = True
            if UserFavorite.objects.filter(user=request.user, fav_id=int(course.course_org.id), fav_type=2):
                has_fav_org = True

        tag = course.tag
        if tag:
            relate_courses = Course.objects.filter(tag=tag)[:1]
        else:
            relate_courses = []
        return render(request, 'course-detail.html', {
            'course': course,
            'relate_courses': relate_courses,
            'has_fav_course': has_fav_course,
            'has_fav_org': has_fav_org,
        })


# class AddFavView(View):
#     """用户收藏及用户取消收藏"""
#
#     def post(self, request):
#         fav_id = request.POST.get('fav_id', 0)
#         fav_type = request.POST.get('fav_type', 0)
#
#         if not request.user.is_authenticated():
#             # 判断用户登录状态
#             return HttpResponse('{"status":"fail", "msg":"用户未登录"}', content_type='application/json')
#
#         exist_records = UserFavorite.objects.filter(user=request.user, fav_id=int(fav_id), fav_type=int(fav_type))
#         if exist_records:
#             # 如果记录已经存在，则表示用户取消收藏
#             exist_records.delete()
#             return HttpResponse('{"status":"success", "msg":"收藏"}', content_type='application/json')
#         else:
#             user_fav = UserFavorite()
#             if int(fav_id) > 0 and int(fav_type) > 0:
#                 user_fav.user = request.user
#                 user_fav.fav_id = int(fav_id)
#                 user_fav.fav_type = int(fav_type)
#                 user_fav.save()
#                 return HttpResponse('{"status":"success", "msg":"已收藏"}', content_type='application/json')
#             else:
#                 return HttpResponse('{"status":"fail", "msg":"收藏出错"}', content_type='application/json')