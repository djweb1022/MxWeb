# -*- coding:utf-8 -*-
__author__ = 'yfj'
__date__ = '2018/10/29 19:31'
from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, min_length=5)
