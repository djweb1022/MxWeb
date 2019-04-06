from django.db import models
from datetime import datetime

from users.models import UserProfile
from courses.models import Course
# Create your models here.


class UserRating(models.Model):
    user = models.ForeignKey(UserProfile, verbose_name=u'用户', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, verbose_name=u'课程', on_delete=models.CASCADE)
    rating = models.IntegerField(default=0, verbose_name=u'用户评分')
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u'添加时间')

    class Meta:
        verbose_name = u'用户评分'
        verbose_name_plural = verbose_name
