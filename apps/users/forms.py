# -*- coding:utf-8 -*-
__author__ = 'yfj'
__date__ = '2018/10/29 19:31'
from django import forms
from captcha.fields import CaptchaField

from .models import UserProfile


class LoginForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, min_length=5)


class RegisterForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, min_length=5)
    captcha = CaptchaField(error_messages={'invalid': u'验证码错误'})


class ForgetForm(forms.Form):
    email = forms.EmailField(required=True)
    # password = forms.CharField(required=True, min_length=5)
    captcha = CaptchaField(error_messages={'invalid': u'验证码错误'})


class ModifyPwdForm(forms.Form):
    # email = forms.EmailField(required=True)
    password1 = forms.CharField(required=True, min_length=5)
    password2 = forms.CharField(required=True, min_length=5)
    # captcha = CaptchaField(error_messages={'invalid': u'验证码错误'})


class UploadImageForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['image']
