from django.shortcuts import render

from django.shortcuts import render
from django.views.generic import View
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.db.models import Q


class InitialView(View):
    def get(self, request):
        return render(request, 'base.html', {})
