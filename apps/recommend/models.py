from django.db import models
from datetime import datetime

from users.models import UserProfile
from courses.models import Course, Lesson, Video
# Create your models here.


class UserRating(models.Model):
    id_int_user = models.IntegerField(default=0, verbose_name=u'用户ID')
    id_int_course = models.IntegerField(default=0, verbose_name=u'课程ID')
    user = models.ForeignKey(UserProfile, verbose_name=u'用户', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, verbose_name=u'课程', on_delete=models.CASCADE)
    rating = models.IntegerField(default=0, verbose_name=u'用户评分')
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')

    class Meta:
        verbose_name = u'用户评分'
        verbose_name_plural = verbose_name


class WatchingTime(models.Model):
    id_int_user = models.IntegerField(default=0, verbose_name=u'用户ID')
    id_int_course = models.IntegerField(default=0, verbose_name=u'课程ID')
    id_int_lesson = models.IntegerField(default=0, verbose_name=u'章节ID')
    id_int_video = models.IntegerField(default=0, verbose_name=u'视频ID')
    user = models.ForeignKey(UserProfile, verbose_name=u'用户', on_delete=models.CASCADE, null=True, blank=True,)
    course = models.ForeignKey(Course, verbose_name=u'课程', on_delete=models.CASCADE, null=True, blank=True,)
    lesson = models.ForeignKey(Lesson, verbose_name=u'章节', on_delete=models.CASCADE, null=True, blank=True,)
    video = models.ForeignKey(Video, verbose_name=u'视频', on_delete=models.CASCADE, null=True, blank=True,)
    time = models.IntegerField(default=0, verbose_name=u'观看时长(秒)')

    time_type = models.CharField(verbose_name=u'时间类别', choices=(('1', u'工作日上午'), ('2', u'工作日下午'), ('3', u'工作日晚间'),
    ('4', u'工作日凌晨'), ('5', u'周末上午'), ('6', u'周末下午'), ('7', u'周末晚间'), ('8', u'周末凌晨'), ('9', u'无')), max_length=20, default=1)

    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')
    # add_time = models.DateTimeField(verbose_name=u'添加时间')

    class Meta:
        verbose_name = u'观看时长'
        verbose_name_plural = verbose_name
