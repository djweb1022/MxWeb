# -*- coding:utf-8 -*-
from django.apps import AppConfig
from django.core import checks
from django.utils.translation import ugettext_lazy as _
import xadmin


class XAdminConfig(AppConfig):
    """Simple AppConfig which does not do automatic discovery."""

    name = 'xadmin'
    # 6-管理
    verbose_name = u"6-管理"

    def ready(self):
        self.module.autodiscover()
        setattr(xadmin,'site',xadmin.site)
