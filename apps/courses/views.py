# -*- coding:utf-8 -*-
from django.shortcuts import render
from django.views.generic import View
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.db.models import Q

from .models import Course, CourseResource, Video
from operation.models import UserFavorite, CourseComments, UserCourse
from recommend.models import UserRating, WatchingTime
from utils.mixin_utils import LoginRequiredMixIn

# Create your views here.


class CourseListView(View):
    def get(self, request):
        all_courses = Course.objects.all().order_by('-add_time')
        hot_courses = Course.objects.all().order_by('-click_nums')[:3]

        # 课程搜索
        search_keywords = request.GET.get('keywords', '')
        if search_keywords:
            all_courses = Course.objects.filter(Q(name__icontains=search_keywords) |
                                                Q(desc__icontains=search_keywords))

        # 统计课程数
        all_courses_nums = all_courses.count()

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
            'all_courses_nums': all_courses_nums,
            'keywords': search_keywords,
        })


class CourseDetailView(View):
    """课程详情页"""
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        # 课程点击数+1
        course.click_nums += 1
        course.save()

        # 用户未登录时，收藏、评分状态置为False
        has_fav_course = False
        has_fav_org = False
        has_rating = False
        rating_value = 0

        # 用户登录后，判断收藏、评分状态
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=int(course.id), fav_type=1):
                has_fav_course = True
            if UserFavorite.objects.filter(user=request.user, fav_id=int(course.course_org.id), fav_type=2):
                has_fav_org = True
            if UserRating.objects.filter(user=request.user, course=course):
                # 若有评分记录，则获得分数，记为rating_value
                has_rating = True
                user_rating = UserRating.objects.get(user=request.user, course=course)
                rating_value = user_rating.rating

        category = course.category
        if category:
            """随机选取标签相同的3个课程"""
            relate_courses = Course.objects.filter(category=category).order_by('?')[:3]
        else:
            relate_courses = []
        return render(request, 'course-detail.html', {
            'course': course,
            'relate_courses': relate_courses,
            'has_fav_course': has_fav_course,
            'has_fav_org': has_fav_org,
            'has_rating': has_rating,
            'rating_value': rating_value,
        })


class CourseInfoView(LoginRequiredMixIn, View):
    """课程章节信息"""
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        # 学习人数点击数+1
        course.students += 1
        course.save()

        # 查询用户是否已经关联了该课程
        user_relate = UserCourse.objects.filter(user=request.user, course=course)
        # 如果没有则建立联系
        if not user_relate:
            user_create_relate = UserCourse(user=request.user, course=course)
            user_create_relate.save()

        # 该同学还学过
        user_courses = UserCourse.objects.filter(course=course)  # 获取“用户课程”表里面该课程的所有记录
        user_ids = [user_course.user.id for user_course in user_courses]  # 获取学过该课程的所有用户id
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)  # 获取这些用户学过的课程记录
        course_ids = [user_course.course_id for user_course in all_user_courses]  # 获取这些课程的id
        relate_courses = Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:5]  # 根据点击量取出5个

        all_resources = CourseResource.objects.filter(course=course)
        return render(request, 'course-video.html', {
            'course': course,
            'course_resources': all_resources,
            'relate_courses': relate_courses,
        })


class CommentView(LoginRequiredMixIn, View):
    """课程评论"""
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))

        # 该同学还学过
        user_courses = UserCourse.objects.filter(course=course)  # 获取“用户课程”表里面该课程的所有记录
        user_ids = [user_course.user.id for user_course in user_courses]  # 获取学过该课程的所有用户id
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)  # 获取这些用户学过的课程记录
        course_ids = [user_course.course_id for user_course in all_user_courses]  # 获取这些课程的id
        relate_courses = Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:5]  # 根据点击量取出5个

        all_resources = CourseResource.objects.filter(course=course)
        all_comments = CourseComments.objects.all().order_by('-add_time')
        return render(request, 'course-comment.html', {
            'course': course,
            'course_resources': all_resources,
            'all_comments': all_comments,
            'relate_courses': relate_courses,
        })


class AddCommentView(View):
    """用户添加评论"""
    def post(self, request):
        if not request.user.is_authenticated():
            # 判断用户登录状态
            return HttpResponse('{"status":"fail", "msg":"用户未登录"}', content_type='application/json')

        course_id = request.POST.get('course_id', 0)
        comments = request.POST.get('comments', '')
        if course_id > 0 and comments:
            course_comments = CourseComments()
            course = Course.objects.get(id=int(course_id))
            course_comments.course = course
            course_comments.comments = comments
            course_comments.user = request.user
            course_comments.save()
            return HttpResponse('{"status":"success", "msg":"添加成功"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail", "msg":"添加失败"}', content_type='application/json')


class VideoPlayView(View):
    def get(self, request, video_id):
        video = Video.objects.get(id=video_id)
        lesson = video.lesson
        course = video.lesson.course
        all_resource = CourseResource.objects.filter(course=course)

        # 查询用户是否已经关联了该数据
        user_course = UserCourse.objects.filter(user=request.user, course=course)
        if not user_course:
            # 如果没有则写入数据库
            my_course = UserCourse(user=request.user, course=course)
            my_course.save()

        # 观看记录保存测试
        # watchingtime = WatchingTime()
        # watchingtime.user = request.user
        # watchingtime.course = course
        # watchingtime.lesson = lesson
        # watchingtime.video = video
        # watchingtime.save()

        # 该同学还学过
        user_courses = UserCourse.objects.filter(course=course)  # 获取“用户课程”表里面该课程的所有记录
        user_ids = [user_course.user.id for user_course in user_courses]  # 获取学过该课程的所有用户id
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)  # 获取这些用户学过的课程记录
        course_ids = [user_course.course_id for user_course in all_user_courses]  # 获取这些课程的id
        relate_courses = Course.objects.filter(id__in=course_ids).order_by('-click_nums')[:5]  # 根据点击量取出5个

        return render(request, 'course-play.html', {
            'course': course,
            'lesson': lesson,
            'course_resources': all_resource,
            'relate_courses': relate_courses,
            'video': video,
        })
