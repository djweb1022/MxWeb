from django.shortcuts import render
from datetime import datetime
import operator

from django.shortcuts import render
from django.views.generic import View
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.db.models import Q
from .models import UserRating, WatchingTime
from courses.models import Course, Lesson, Video
from utils.mixin_utils import LoginRequiredMixIn
import json, math
import numpy as np
import pandas as pd
import keras_metrics as km
from keras.models import load_model
import os
import keras


def load_predict(pre_list):
    # 清除session，避免重复调用出错
    keras.backend.clear_session()
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(BASE_DIR, 'recommend', 'model.h5')
    model = load_model(model_path,
                       custom_objects={'binary_precision': km.binary_precision(),
                                       'binary_recall': km.binary_recall(),
                                       'binary_f1_score': km.f1_score()})
    predictions = model.predict(pre_list)
    print(predictions)
    return predictions


class InitialView(LoginRequiredMixIn, View):
    def get(self, request):

        user = request.user

        # 获取现在时间，提取小时、星期，判断时间类型
        get_time = get_now_time()
        hour = get_time.hour
        weekday = get_time.weekday()+2
        time_type = get_time_type_num(weekday, hour)

        # 调用函数获得提示语
        time_turple = get_time_type(weekday, hour)
        string_type = time_turple[0]
        string_tag = time_turple[1]

        """下面统计观看时间最长的时间类型，作为该用户最喜欢的时间情境"""
        user_watchingtime = WatchingTime.objects.filter(id_int_user=request.user.id)
        if user_watchingtime.exists():
            list_timetype = []
            list_type_value = []
            # 获取所有已经出现的时间类型，组成列表
            for record in user_watchingtime:
                list_timetype.append(record.time_type)
            # 去除列表中的重复值
            list_timetype = list(set(list_timetype))
            # 列表排序
            list_timetype = sorted(list_timetype)
            # 分类统计观看时长，返回嵌套列表
            list_type_value_count = 0
            for single_type in list_timetype:
                # print(single_type)
                user_type_watchingtime = WatchingTime.objects.filter(id_int_user=request.user.id, time_type=single_type)
                sum_time = 0
                for record_user_type_watchingtime in user_type_watchingtime:
                    sum_time += record_user_type_watchingtime.time
                a = [single_type, sum_time]
                list_type_value.append(a)
                list_type_value_count += 1

            # 嵌套列表按字列表第二个值——时间总和 进行排序
            # print(list_type_value)
            list_type_value = sorted(list_type_value, key=operator.itemgetter(1), reverse=True)
            # print(list_type_value)
            # print(list_type_value_count)

            # 获取嵌套列表中的第一项，也就是时间总和最长的类型和秒数
            max_type = int(list_type_value[0][0])
            max_time = int(list_type_value[0][1])

            # 调用函数，获得最大时间类型对应提示语
            max_turple = get_max_type_return(max_type)
            string_max_type = max_turple[0]
            string_max_tag = max_turple[1]
        else:
            max_turple = get_max_type_return(9)
            string_max_type = max_turple[0]
            string_max_tag = max_turple[1]
            list_type_value = [['9', 0]]

        """扇形图:遍历嵌套列表"""
        list_record_type = []
        list_record_seconds = []
        for list_type_value_record in list_type_value:
            record_type = int(list_type_value_record[0])
            record_seconds = int(list_type_value_record[1])
            list_record_type.append(record_type)
            list_record_seconds.append(record_seconds)
        # print(list_record_type)
        # print(list_record_seconds)

        # 将数字列表转化为相应的文字列表，将秒数列表转化为分钟列表
        list_type_word = []
        list_type_minute = []
        for record_type in list_record_type:
            type_word = str(get_max_type_return(record_type)[0])
            list_type_word.append(type_word)
        for record_seconds in list_record_seconds:
            record_minutes = record_seconds // 60
            list_type_minute.append(record_minutes)
        # print(list_type_word)
        # print(list_type_minute)
        # 按echart要求列表嵌套字典
        list_value_name = []
        for i in range(0, len(list_type_word)):
            dict_value_name = {'value': list_type_minute[i], 'name': list_type_word[i]}
            list_value_name.append(dict_value_name)
        # print(list_value_name)

        """散点图:首先提取用户观看记录的星期、小时、秒数，装入列表，找出最大秒数用于调整散点大小"""
        list_week_hour_second = []
        list_second_for_max = []

        if user_watchingtime.exists():
            for record in user_watchingtime:
                week_1 = record.add_time.weekday()
                hour_1 = record.add_time.hour
                timesecond = record.time
                a_1 = [week_1, hour_1, timesecond]
                list_week_hour_second.append(a_1)

            list_minute_for_max = []
            list_week_hour_secondsum = []
            for week_2 in range(0, 7):
                for hour_2 in range(0, 24):
                    second_sum = 0
                    # minute_sum = 0
                    for record in list_week_hour_second:
                        if week_2 == int(record[0]) and hour_2 == int(record[1]):
                            second_sum += int(record[2])
                    minute_sum = second_sum // 60
                    list_minute_for_max.append(minute_sum)
                    a_2 = [week_2, hour_2, minute_sum]
                    list_week_hour_secondsum.append(a_2)
                    # minute_sum_sum += minute_sum

            max_minute = max(list_minute_for_max)
            # 生成散点调整大小，目前单位最长时间低于15分钟，维持suitsize=4，若超过15分钟，则换算缩放倍数
            suitsize = 0
            if 0 <= max_minute <= 15:
                suitsize = 4
            elif max_minute > 15:
                suitsize = 15 / max_minute
                suitsize = '%.2f' % suitsize
                suitsize = float(suitsize) * 4
            print(suitsize)

        else:
            list_week_hour_secondsum = [[0, 0, 0]]
            suitsize = 4

            print(list_week_hour_secondsum)
            print(len(list_week_hour_secondsum))
            # print(minute_sum_sum)

        """遍历所有课程，用训练好的DeepCA模型预测分数"""
        user_id_list = []
        course_id_list = []
        time_type_list = []
        time_list = []
        time_second_list = []
        for course_id in range(1, 37):
            predict_records = WatchingTime.objects.filter(id_int_user=request.user.id, id_int_course=course_id)
            if predict_records.exists():
                sum_second = 0
                num_count = predict_records.count()
                for predict_record in predict_records:
                    sum_second += predict_record.time

                # 先求用户平均观看该课程的时长，后转化为时间标签
                avg_second = int(sum_second / num_count)
                sum_second_label = int(avg_second // 10 + 1)
                # avg_minute = int(avg_second // 60)

                user_id_list.append(request.user.id)
                course_id_list.append(course_id)
                time_type_list.append(time_type)
                time_list.append(sum_second_label)
                time_second_list.append(avg_second)
            else:
                user_id_list.append(request.user.id)
                course_id_list.append(course_id)
                time_type_list.append(time_type)
                time_list.append(1)

        train_1 = np.array(user_id_list)
        train_2 = np.array(course_id_list)
        train_3 = np.array(time_type_list)
        train_4 = np.array(time_list)

        train_1_2d = train_1.reshape((train_1.shape[0], 1))
        train_2_2d = train_2.reshape((train_2.shape[0], 1))
        train_3_2d = train_3.reshape((train_3.shape[0], 1))
        train_4_2d = train_4.reshape((train_4.shape[0], 1))

        list_train_4 = [train_1_2d, train_2_2d, train_3_2d, train_4_2d]
        predictions_list_2d = load_predict(list_train_4)
        predictions_list_1d = predictions_list_2d.reshape((predictions_list_2d.shape[0], ))

        courseid_predictions_dict = {
            'course_id': train_2,
            'predictions': predictions_list_1d,
            'time': time_second_list,
        }
        courseid_predictions_index = range(len(train_2))

        courseid_predictions_df = pd.DataFrame(courseid_predictions_dict, courseid_predictions_index)
        courseid_predictions_df_descend = courseid_predictions_df.sort_values(by='predictions', ascending=False)

        courseid_descend = list(courseid_predictions_df_descend['course_id'])
        score_descend = list(courseid_predictions_df_descend['predictions'])
        time_descend = list(courseid_predictions_df_descend['time'])
        courseobj = Course.objects.filter(id__in=courseid_descend)
        courseobj_dict = {obj.id: obj for obj in courseobj}
        courseobj_sorted = [courseobj_dict[id] for id in courseid_descend]
        num_count = 0
        for courseobj in courseobj_sorted:
            courseobj.score = score_descend[num_count]
            courseobj.time = time_descend[num_count]
            num_count += 1

        return render(request, 'recommend-initial.html', {
            'user': user,
            'string_type': string_type,
            'string_tag': string_tag,
            'string_max_type': string_max_type,
            'string_max_tag': string_max_tag,
            # 'list_type_word': list_type_word,
            # 'list_value_name': list_value_name,
            'list_type_word': json.dumps(list_type_word),
            'list_value_name': json.dumps(list_value_name),
            'list_week_hour_secondsum': json.dumps(list_week_hour_secondsum),
            'suitsize': suitsize,
            'courseobj_sorted': courseobj_sorted,
        })


class Gettime(View):
    """返回当前时间、情境"""

    def post(self, request):
        get_time = get_now_time()
        year = get_time.year
        month = get_time.month
        day = get_time.day
        hour = get_time.hour
        minute = get_time.minute
        second = get_time.second

        # 若时、分、秒在0-9之间，前面加个0再显示
        def zeronum(num):
            if 0 <= int(num) <= 9:
                num = '0' + str(num)
            return num

        hour = zeronum(hour)
        minute = zeronum(minute)
        second = zeronum(second)

        string_now = '%d年%d月%d日 %s:%s:%s' % (year, month, day, hour, minute, second)

        data = {
            'string_now': string_now,
        }

        # return HttpResponse('{"status":"success"}', second)

        return HttpResponse(json.dumps(data), content_type='application/json')


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


class AddTime(View):
    """用户观看时长保存"""

    def post(self, request):
        """通过ajax获得前端传来的数据"""
        course_id = request.POST.get('course_id', 0)
        lesson_id = request.POST.get('lesson_id', 0)
        video_id = request.POST.get('video_id', 0)
        timevalue = request.POST.get('sTime', 0)

        """根据id进行实例化"""
        course = Course.objects.get(id=int(course_id))
        lesson = Lesson.objects.get(id=int(lesson_id))
        video = Video.objects.get(id=int(video_id))

        if int(course_id) > 0 and int(lesson_id) > 0 and int(video_id) > 0 and int(timevalue) >= 0:
            watchingtime = WatchingTime()
            watchingtime.id_int_user = request.user.id
            watchingtime.id_int_course = course_id
            watchingtime.id_int_lesson = lesson_id
            watchingtime.id_int_video = video_id
            # watchingtime.user = request.user
            # watchingtime.course = course
            # watchingtime.lesson = lesson
            # watchingtime.video = video
            watchingtime.time = timevalue

            # 获得目前的时间
            get_time = datetime.now()

            # 设定调试时间
            # get_time = datetime(2019, 3, 22, 18, 34, 55)

            # 保存时间为目前获得的时间，提取星期、小时的值
            watchingtime.add_time = get_time
            weekday = get_time.weekday()
            hour = get_time.hour

            watchingtime.time_type = get_time_type_num(weekday, hour)

            # 指定保存时间为2019年3月22日12时34分55秒
            # watchingtime.add_time = datetime(2019, 3, 22, 12, 34, 55)

            watchingtime.save()
            return HttpResponse('{"status":"success", "value":"已保存"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail", "msg":"不保存"}', content_type='application/json')


def get_now_time():
    """获得目前时间"""
    get_time = datetime.now()

    # 指定当前时间为2019年3月22日12时34分55秒
    # get_time = datetime(2019, 3, 22, 12, 34, 55)

    return get_time


def get_time_type_num(weekday_1, hour_1):
    """传入星期、小时，对当前情境类别作判断，返回编号"""
    if 0 <= int(weekday_1) <= 4:
        if 6 <= int(hour_1) <= 11:
            time_type = 1
        elif 12 <= int(hour_1) <= 17:
            time_type = 2
        elif 18 <= int(hour_1) <= 23:
            time_type = 3
        elif 0 <= int(hour_1) <= 5:
            time_type = 4
        else:
            time_type = 9
    elif 5 <= int(weekday_1) <= 6:
        if 6 <= int(hour_1) <= 11:
            time_type = 5
        elif 12 <= int(hour_1) <= 17:
            time_type = 6
        elif 18 <= int(hour_1) <= 23:
            time_type = 7
        elif 0 <= int(hour_1) <= 5:
            time_type = 8
        else:
            time_type = 9
    else:
        time_type = 9

    return time_type


def get_time_type(weekday_1, hour_1):
    """传入星期、小时，对当前情境类别作判断，返回提示语"""
    if 0 <= int(weekday_1) <= 4:
        if 6 <= int(hour_1) <= 11:
            string_type_1 = '工作日上午'
            string_tag_1 = '区间：周一至周五 每天6:00-11:59'
        elif 12 <= int(hour_1) <= 17:
            string_type_1 = '工作日下午'
            string_tag_1 = '区间：周一至周五 每天12:00-17:59'
        elif 18 <= int(hour_1) <= 23:
            string_type_1 = '工作日晚间'
            string_tag_1 = '区间：周一至周五 每天18:00-23:59'
        elif 0 <= int(hour_1) <= 5:
            string_type_1 = '工作日凌晨'
            string_tag_1 = '区间：周一至周五 每天0:00-5:59'
        else:
            string_type_1 = '无情境'
            string_tag_1 = '无区间'
    elif 5 <= int(weekday_1) <= 6:
        if 6 <= int(hour_1) <= 11:
            string_type_1 = '周末上午'
            string_tag_1 = '区间：周六和周日 每天6:00-11:59'
        elif 12 <= int(hour_1) <= 17:
            string_type_1 = '周末下午'
            string_tag_1 = '区间：周六和周日 每天12:00-17:59'
        elif 18 <= int(hour_1) <= 23:
            string_type_1 = '周末晚间'
            string_tag_1 = '区间：周六和周日 每天18:00-23:59'
        elif 0 <= int(hour_1) <= 5:
            string_type_1 = '周末凌晨'
            string_tag_1 = '区间：周六和周日 每天0:00-5:59'
        else:
            string_type_1 = '无情境'
            string_tag_1 = '无区间'
    else:
        string_type_1 = '无情境'
        string_tag_1 = '无区间'

    return string_type_1, string_tag_1


def get_max_type_return(max_type_1):
    """传入最大时间类型，返回提示语"""
    max_turple_1 = ()

    if max_type_1 == 1:
        max_turple_1 = get_time_type(0, 6)
    elif max_type_1 == 2:
        max_turple_1 = get_time_type(0, 12)
    elif max_type_1 == 3:
        max_turple_1 = get_time_type(0, 18)
    elif max_type_1 == 4:
        max_turple_1 = get_time_type(0, 0)
    elif max_type_1 == 5:
        max_turple_1 = get_time_type(5, 6)
    elif max_type_1 == 6:
        max_turple_1 = get_time_type(5, 12)
    elif max_type_1 == 7:
        max_turple_1 = get_time_type(5, 18)
    elif max_type_1 == 8:
        max_turple_1 = get_time_type(5, 0)
    elif max_type_1 == 9:
        max_turple_1 = get_time_type(-1, -1)

    string_max_type_1 = max_turple_1[0]
    string_max_tag_1 = max_turple_1[1]

    return string_max_type_1, string_max_tag_1


def get_hour_minute_second(seconds):
    """传入秒数，转化为x小时x分钟x秒"""
    hour = 0
    minute = 0
    second = 0
    if seconds // 60:
        minute = seconds // 60
        second = seconds % 60
        if minute // 60:
            hour = minute // 60
            minute = minute % 60
        else:
            pass
    else:
        second = seconds
    return hour, minute, second
