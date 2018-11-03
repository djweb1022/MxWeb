# -*- coding:utf-8 -*-
__author__ = 'yfj'
__date__ = '2018/11/3 14:46'
from django import forms

from operation.models import UserAsk


# class UserAskForm(forms.Form):
#     name = forms.CharField(required=True, min_length=2, max_length=20)
#     phone = forms.CharField(required=True, min_length=11, max_length=11)
#     course_name = forms.CharField(required=True, min_length=5, max_length=50)


class UserAskForm(forms.ModelForm):
    class Meta:
        model = UserAsk  # 继承UserAsk的form
        fields = ['name', 'mobile', 'course_name']