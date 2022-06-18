# -*- coding: utf-8 -*-
# @Time : 2019/6/9 15:09 
# @Author : Arjun
# @Site :  
# @File : handle_times.py 
# @Software: PyCharm
import time
import datetime


class TweetTime(object):

    @staticmethod
    def cst_to_str(cstTime):
        tempTime = time.strptime(cstTime, '%a %b %d %H:%M:%S +0000 %Y')
        resTime = time.strftime("%H:%M:%S-%Y/%m/%d", tempTime)
        return resTime


    @staticmethod
    def cst_to_time(cstTime):
        tempTime = time.strptime(cstTime, '%a %b %d %H:%M:%S +0000 %Y')
        resTime = time.strftime("%Y-%m-%d %H:%M:%S", tempTime)
        timeArray = time.strptime(resTime, "%Y-%m-%d %H:%M:%S")
        timeStamp = int(time.mktime(timeArray)) + 8 * 60 * 60
        return timeStamp

    @staticmethod
    def get_current_week():
        monday = datetime.date.today()
        one_day = datetime.timedelta(days=1)
        while monday.weekday() != 0:
            monday -= one_day
        timeArray = time.strptime(str(monday), "%Y-%m-%d")
        timestamp = int(time.mktime(timeArray))
        timestamp = timestamp - 7 * 24 * 60 * 60
        return timestamp

    @staticmethod
    def strip_str(value):
        if value:
            if type(value) == list:
                value = "".join(value)
            return value.replace('\n', '') \
                .replace('\t', '') \
                .replace('\xa0', '') \
                .replace('\r', '') \
                .replace("<br />", "") \
                .replace("\u3000", " ") \
                .replace("<br/>", "").strip()
        else:
            return None


tweet_time = TweetTime()

