# -*- coding: utf-8 -*-
# @Time    : 2020/2/1 17:01
# @Author  : Arjun


import time
import datetime


class TweetTime(object):
    """
    转化成北京时间
    """
    @staticmethod
    def handle_created_at(cstTime):
        tempTime = time.strptime(cstTime, '%a %b %d %H:%M:%S +0000 %Y')
        resTime = time.strftime("%H:%M:%S-%Y/%m/%d", tempTime)
        return resTime

    @staticmethod
    def cst_to_str(cstTime):
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


tweet_time = TweetTime()

