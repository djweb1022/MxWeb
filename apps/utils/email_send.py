# -*- coding:utf-8 -*-
__author__ = 'yfj'
__date__ = '2018/10/30 11:00'

from random import Random

from users.models import EmailVerifyRecord

def send_register_email(email, type=0):
    email_record = EmailVerifyRecord()
    random_str =


def generate_random_str():


def random_str(randomlength=8):
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars)-1
    random = Random()
    for i in range(randomlength):
        str+=chars[random.randint(0,length)]
    return str