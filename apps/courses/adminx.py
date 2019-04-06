# -*- coding:utf-8 -*-
__author__ = 'yfj'
__date__ = '2018/10/25 15:51'

import xadmin

from .models import Course, Lesson, Video, CourseResource, BannerCourse


class LessonInline(object):
    model = Lesson
    extra = 0


class CourseResourceInline(object):
    model = CourseResource
    extra = 0


class VideoInline(object):
    model = Video
    extra = 0


class CourseAdmin(object):
    list_display = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students', 'click_nums', 'get_zj_nums']
    search_fields = ['name', 'desc', 'detail', 'degree', 'students']
    list_filter = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students']

    # 默认按点击数排序
    ordering = ['-click_nums']

    # 使用ueditor
    # style_fields = {'detail': 'ueditor'}

    # 将添加课程与添加章节、添加课程资源放在同一页面
    inlines = [LessonInline, CourseResourceInline]

    # 直接在列表页添加修改功能
    list_editable = ['degree', 'desc']

    # 设置为只读，数据不可更改
    # readonly_fields = ['click_nums']

    # 设置为不可见
    # exclude = ['click_nums']

    # 启用外键搜索模式
    # relfield_style = 'fk-ajax'

    # 启用外键选择模式
    # relfield_style = 'fk-select'

    # 设置自动刷新时间
    refresh_times = [3, 5]

    # 运用重载仅显示非轮播课程数据
    def queryset(self):
        qs = super(CourseAdmin, self).queryset()
        qs = qs.filter(is_banner=False)
        return qs

    def save_models(self):
        # 重载save_models，在保存课程的时候统计机构课程的课程数
        obj = self.new_obj
        obj.save()
        if obj.course_org is not None:
            course_org = obj.course_org
            course_org.course_nums = Course.objects.filter(course_org=course_org).count()
            course_org.save()

    # 开启excel导入功能
    # import_excel = True
    #
    # def post(self, request, *args, **kwargs):
    #     if 'excel' in request.FILES:
    #         pass
    #     # 必须返回，不然报错（或者注释掉）
    #     return super(CourseAdmin, self).post(request, *args, **kwargs)


# 格式和CourseAdmin相同
class BannerCourseAdmin(object):
    list_display = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students', 'click_nums', 'get_zj_nums']
    search_fields = ['name', 'desc', 'detail', 'degree', 'students']
    list_filter = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students']
    ordering = ['-click_nums']
    inlines = [LessonInline, CourseResourceInline]

    # 使用ueditor
    # style_fields = {'detail': 'ueditor'}


# 运用重载仅显示轮播课程数据
    def queryset(self):
        qs = super(BannerCourseAdmin, self).queryset()
        qs = qs.filter(is_banner=True)
        return qs


class LessonAdmin(object):
    list_display = ['course', 'name', 'add_time']
    search_fields = ['course', 'name']
    list_filter = ['course__name', 'name', 'add_time']
    inlines = [VideoInline]
    # model_icon = 'fa fa-envelope'


class VideoAdmin(object):
    list_display = ['lesson', 'name', 'add_time', 'learn_times', 'url']
    search_fields = ['lesson', 'name']
    list_filter = ['lesson', 'name', 'add_time', 'learn_times', 'url']


class CourseResourceAdmin(object):
    list_display = ['course', 'name', 'download', 'add_time']
    search_fields = ['course', 'name', 'download']
    list_filter = ['course', 'name', 'download', 'add_time']


xadmin.site.register(Course, CourseAdmin)
xadmin.site.register(BannerCourse, BannerCourseAdmin)
xadmin.site.register(Lesson, LessonAdmin)
xadmin.site.register(Video, VideoAdmin)
xadmin.site.register(CourseResource, CourseResourceAdmin)

