# -*- coding:utf-8 -*-
"""MxWeb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView
from django.views.static import serve
import xadmin

# from users.views import user_login  #基于函数方法的书写
from users.views import LoginView, RegisterView, ActiveUserView, ForgetPwdView, ResetView, ModifyPwdView, LogoutView, IndexView  # 基于类的书写
from organization.views import OrgView
from MxWeb.settings import MEDIA_ROOT
# from MxWeb.settings import STATIC_ROOT


urlpatterns = [
    url(r'^xadmin/', xadmin.site.urls),
    url(r'^$', IndexView.as_view(), name='index'),
    # url(r'^login/$', TemplateView.as_view(template_name='login.html'), name='login'),
    # url(r'^login/$', user_login, name='login'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^active/(?P<active_code>.*)/$', ActiveUserView.as_view(), name='user_active'),
    url(r'^forget/$', ForgetPwdView.as_view(), name='forget_pwd'),
    # 重置密码链接
    url(r'^reset/(?P<active_code>.*)/$', ResetView.as_view(), name='reset_pwd'),

    url(r'^modify_pwd/$', ModifyPwdView.as_view(), name='modify_pwd'),

    # 课程机构url配置
    url(r'^org/', include('organization.urls', namespace='org')),

    # 课程相关url配置
    url(r'^course/', include('courses.urls', namespace='course')),

    # 配置上传文件的访问处理函数
    url(r'^media/(?P<path>.*)/$', serve, {'document_root': MEDIA_ROOT}),

    # # 配置用于全局404调试的静态文件访问处理函数
    # url(r'^static/(?P<path>.*)/$', serve, {'document_root': STATIC_ROOT}),

    # 用户相关url配置
    url(r'^users/', include('users.urls', namespace='users')),

    # 推荐系统url配置
    url(r'^recommend/', include('recommend.urls', namespace='recommend')),

    # 富文本相关url
    # url(r'^ueditor/', include('DjangoUeditor.urls')),
]

# 全局404页面配置
handler404 = 'users.views.page_not_found'

# 全局500页面配置
handler500 = 'users.views.page_error'
