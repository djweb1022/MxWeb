# -*- coding:utf-8 -*-
import json
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.views.generic import View
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, HttpResponseRedirect
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse

from .models import UserProfile, EmailVerifyRecord, Banner
from operation.models import UserCourse, UserFavorite, UserMessage
from .forms import LoginForm, RegisterForm, ForgetForm, ModifyPwdForm, UploadImageForm, UserInfoForm
from utils.email_send import send_register_email
from utils.mixin_utils import LoginRequiredMixIn
from organization.models import CourseOrg, Teacher
from courses.models import Course

# Create your views here.


class CustomBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(Q(username=username) | Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class ActiveUserView(View):
    """用户激活"""
    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                user = UserProfile.objects.get(email=email)
                user.is_active = True
                user.save()
        else:
            return render(request, 'active_fail.html')
        return render(request, 'login.html')


class RegisterView(View):
    """用户注册"""
    def get(self, request):
        register_form = RegisterForm()
        return render(request, 'register.html', {'register_form': register_form})

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            user_name = request.POST.get('email', '')
            if UserProfile.objects.filter(email=user_name):
                return render(request, 'register.html', {'register_form': register_form, 'msg': '用户已经存在'})
            pass_word = request.POST.get('password', '')
            user_profile = UserProfile()
            user_profile.username = user_name
            user_profile.email = user_name
            user_profile.is_active = False
            user_profile.password = make_password(pass_word)
            user_profile.save()

            # 写入欢迎注册消息
            user_message = UserMessage()
            user_message.user = user_profile.id
            user_message.message = '欢迎注册！'
            user_message.save()

            send_register_email(user_name, 'register')
            return render(request, 'login.html', {'msg': '激活邮件已发送！'})
        else:
            return render(request, 'register.html', {'register_form': register_form})


class LogoutView(View):
    """用户登出"""
    def get(self, request):
        logout(request)

        return HttpResponseRedirect(reverse('index'))


class LoginView(View):
    """用户登录"""
    def get(self, request):
        return render(request, 'login.html', {})

    def post(self, request):
        login_form = LoginForm(request.POST)  # 加断点可查看min_length=5是否有效
        if login_form.is_valid():
            user_name = request.POST.get('username', '')
            pass_word = request.POST.get('password', '')
            # pass
            user = authenticate(username=user_name, password=pass_word)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    # return render(request, 'index.html') 数据无法返回
                    return HttpResponseRedirect(reverse('index'))
                else:
                    return render(request, 'login.html', {'msg': '用户未激活！'})
            else:
                return render(request, 'login.html', {'msg': '用户名或密码错误！'})
        else:
            return render(request, 'login.html', {'login_form': login_form})


class ForgetPwdView(View):
    def get(self, request):
        forget_form = ForgetForm()
        return render(request, 'forgetpwd.html', {'forget_form': forget_form})

    def post(self, request):
        forget_form = ForgetForm(request.POST)
        if forget_form.is_valid():
            email = request.POST.get('email', '')
            if not UserProfile.objects.filter(email=email):
                return render(request, 'forgetpwd.html', {'forget_form': forget_form, 'msg': '用户不存在'})
            send_register_email(email, 'forget')
            return render(request, 'send_success.html')
        else:
            return render(request, 'forgetpwd.html', {'forget_form': forget_form})


class ResetView(View):
    """进入密码重置页面(未登录时)"""
    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        user_click = EmailVerifyRecord.objects.get(code=active_code)
        if user_click.is_click is True:
            return render(request, 'clicked.html')
        if all_records:
            for record in all_records:
                email = record.email
                return render(request, 'password_reset.html', {'email': email, 'active_code': active_code})
        else:
            return render(request, 'active_fail.html')
        return render(request, 'login.html')


class ModifyPwdView(View):
    """修改用户密码，表单逻辑(未登录时)"""
    def post(self, request):
        active_code = request.POST.get('active_code', '')
        user_click = EmailVerifyRecord.objects.get(code=active_code)
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get('password1', '')
            pwd2 = request.POST.get('password2', '')
            email = request.POST.get('email', '')
            if pwd1 != pwd2:
                return render(request, 'password_reset.html', {'email': email, 'msg': '密码不一致！'})
            user = UserProfile.objects.get(email=email)
            user.password = make_password(pwd2)
            user.save()
            user_click.is_click = True
            user_click.save()
            return render(request, 'login.html')
        else:
            email = request.POST.get('email', '')
            return render(request, 'password_reset.html', {'email': email, 'modify_form': modify_form})


# def user_login(request):
#     if request.method == 'POST':
#         user_name = request.POST.get('username', '')
#         pass_word = request.POST.get('password', '')
#         # pass
#         user = authenticate(username=user_name, password=pass_word)
#         if user is not None:
#             login(request, user)
#             return render(request, 'index.html')
#         else:
#             return render(request, 'login.html', {'msg': '用户名或密码错误！'})
#     elif request.method == 'GET':
#         return render(request, 'login.html', {})
# 用函数的方式书写Login逻辑，替换为基于类来实现 6-4
# 6-6 finish

class UserinfoView(LoginRequiredMixIn, View):
    """用户个人信息"""
    def get(self, request):
        return render(request, 'usercenter-info.html', {})

    def post(self, request):
        user_info_form = UserInfoForm(request.POST, instance=request.user)
        if user_info_form.is_valid():
            user_info_form.save()
            return HttpResponse('{"status": "success"}', content_type='application/json')
        else:
            return HttpResponse(json.dumps(user_info_form.errors), content_type='application/json')


class UploadImageView(LoginRequiredMixIn, View):
    """用户修改头像"""
    def post(self, request):
        image_form = UploadImageForm(request.POST, request.FILES, instance=request.user)
        if image_form.is_valid():
            # image = image_form.cleaned_data['image']
            # request.user.image = image
            image_form.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail"}', content_type='application/json')


class UpdatePwdView(View):
    """在个人中心修改用户密码(已登录)"""
    def post(self, request):
        # active_code = request.POST.get('active_code', '')
        # user_click = EmailVerifyRecord.objects.get(code=active_code)
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get('password1', '')
            pwd2 = request.POST.get('password2', '')
            # email = request.POST.get('email', '')
            if pwd1 != pwd2:
                return HttpResponse('{"status": "fail", "msg": "密码不一致！"}', content_type='application/json')
            user = request.user
            user.password = make_password(pwd2)
            user.save()
            # user_click.is_click = True
            # user_click.save()
            return HttpResponse('{"status": "success", "msg": "修改成功！"}', content_type='application/json')
        else:
            # email = request.POST.get('email', '')
            return HttpResponse(json.dumps(modify_form.errors), content_type='application/json')


class SendEmailCodeView(LoginRequiredMixIn, View):
    """发送邮箱验证码"""
    def get(self, request):
        email = request.GET.get('email', '')

        if UserProfile.objects.filter(email=email):
            return HttpResponse('{"email": "邮箱已经存在"}', content_type='application/json')
        send_register_email(email, 'update_email')
        return HttpResponse('{"status": "success"}', content_type='application/json')


class UpdateEmailView(LoginRequiredMixIn, View):
    """修改个人邮箱"""
    def post(self, request):
        email = request.POST.get('email', '')
        code = request.POST.get('code', '')

        existed_records = EmailVerifyRecord.objects.filter(email=email, code=code, send_type='update_email')
        if existed_records:
            user = request.user
            user.email = email
            user.save()
            return HttpResponse('{"status": "success"}', content_type='application/json')
        else:
            return HttpResponse('{"email": "验证码出错"}', content_type='application/json')


class MyCourseView(LoginRequiredMixIn, View):
    """我的课程"""
    def get(self, request):
        user_courses = UserCourse.objects.filter(user=request.user)

        # 分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(user_courses, 4, request=request)
        courses = p.page(page)

        return render(request, 'usercenter-mycourse.html', {
            'user_courses': courses,
        })


class MyFavOrgView(LoginRequiredMixIn, View):
    """我收藏的课程机构"""
    def get(self, request):
        org_list = []
        fav_orgs = UserFavorite.objects.filter(user=request.user, fav_type=2)
        for fav_org in fav_orgs:
            org_id = fav_org.fav_id
            org = CourseOrg.objects.get(id=org_id)
            org_list.append(org)

        # 分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(org_list, 4, request=request)
        org_page = p.page(page)

        return render(request, 'usercenter-fav-org.html', {
            'org_list': org_page,
        })


class MyFavTeacherView(LoginRequiredMixIn, View):
    """我收藏的授课教师"""
    def get(self, request):
        teacher_list = []
        fav_teachers = UserFavorite.objects.filter(user=request.user, fav_type=3)
        for fav_teacher in fav_teachers:
            teacher_id = fav_teacher.fav_id
            teacher = Teacher.objects.get(id=teacher_id)
            teacher_list.append(teacher)

        # 分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(teacher_list, 4, request=request)
        teacher_page = p.page(page)

        return render(request, 'usercenter-fav-teacher.html', {
            'teacher_list': teacher_page,
        })


class MyFavCourseView(LoginRequiredMixIn, View):
    """我收藏的课程"""
    def get(self, request):
        course_list = []
        fav_courses = UserFavorite.objects.filter(user=request.user, fav_type=1)
        for fav_course in fav_courses:
            course_id = fav_course.fav_id
            course = Course.objects.get(id=course_id)
            course_list.append(course)

        # 分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(course_list, 4, request=request)
        course_page = p.page(page)

        return render(request, 'usercenter-fav-course.html', {
            'course_list': course_page,
        })


class MymessageView(LoginRequiredMixIn, View):
    """我的消息"""
    def get(self, request):
        all_messages = UserMessage.objects.filter(user=request.user.id).order_by('-add_time')

        # 用户进入个人消息后清空未读
        all_unread_messages = UserMessage.objects.filter(user=request.user.id, has_read=False)
        for all_unread_message in all_unread_messages:
            all_unread_message.has_read = True
            all_unread_message.save()

        # 分页
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_messages, 4, request=request)
        messages = p.page(page)

        return render(request, 'usercenter-message.html', {
            'messages': messages
        })


class IndexView(View):
    # 访问首页
    def get(self, request):
        # 取出轮播图

        # 全局500测试
        # print 1/0
        all_banners = Banner.objects.all().order_by('index')
        courses = Course.objects.filter(is_banner=False).order_by('-students')[:6]
        banner_courses = Course.objects.filter(is_banner=True).order_by('-add_time')[:3]
        course_orgs = CourseOrg.objects.all()[:15]
        return render(request, 'index.html', {
            'all_banners': all_banners,
            'courses': courses,
            'banner_courses': banner_courses,
            'course_orgs': course_orgs,
        })


def page_not_found(request):
    # 全局404处理函数
    from django.shortcuts import render_to_response
    response = render_to_response('404.html', {})
    response.status_code = 404
    return response


def page_error(request):
    # 全局500处理函数
    from django.shortcuts import render_to_response
    response = render_to_response('500.html', {})
    response.status_code = 500
    return response
