from django.shortcuts import render

from django.shortcuts import render
from django.views.generic import View
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.db.models import Q
from .models import UserRating
from courses.models import Course


class InitialView(View):
    def get(self, request):
        return render(request, 'base.html', {})


class AddRating(View):
    """用户评分"""
    def post(self, request):
        rating_id = request.POST.get('rating_id', 0)
        rating_value = request.POST.get('rating_value', 0)

        course = Course.objects.get(id=int(rating_id))

        if not request.user.is_authenticated():
            # 判断用户登录状态
            return HttpResponse('{"status":"fail", "msg":"用户未登录"}', content_type='application/json')

        exist_records = UserRating.objects.filter(user=request.user, course=course)
        if exist_records:
            # 若用户已经对课程评过分，则删除已有评分
            exist_records.delete()

        user_rating = UserRating()
        if int(rating_id) > 0 and int(rating_value) > 0:
            user_rating.id_int_user = request.user.id
            user_rating.id_int_course = rating_id
            user_rating.user = request.user
            user_rating.course = course
            user_rating.rating = rating_value
            user_rating.save()
            return HttpResponse('{"status":"success", "msg":"已评分"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail", "msg":"评分出错"}', content_type='application/json')
