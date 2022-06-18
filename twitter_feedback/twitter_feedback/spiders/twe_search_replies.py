# -*- coding: utf-8 -*-
import random
import scrapy
from ..settings import REDIS_HOST, REDIS_PORT, REDIS_PARAMS, REDIS_TOKEN_DB, REPLIES_TABLE, TWITTER_APIS_KEY
from ..settings import MIN_SCORE, ERROR_CODE_401, ERROR_CODE_403, ERROR_CODE_429, ALLOWED_CODE
from scrapy_redis.spiders import RedisSpider
import redis
from copy import deepcopy
from dingtalkchatbot.chatbot import DingtalkChatbot
from scrapy.exceptions import CloseSpider
import json
import re
from ..items import Replies
from urllib.parse import quote
from ..tools.handle_times import tweet_time
import time
import datetime
from ..settings import REPLIES_REDIS_KEY


class TweSearchRepliesSpider(RedisSpider):
    """
    获取评论

    from 在库用户主动回复别人
    to   其他人主动回复在库人
    """
    name = 'twe_search_replies'
    allowed_domains = ['twitter.com']
    start_urls = [
        # 'https://api.twitter.com/1.1/search/tweets.json?q=to%3AHuPing1&include_ext_alt_text=true&include_entities=true&result_type=recent&count=100',
        # 'https://api.twitter.com/1.1/search/tweets.json?q=to%3Asbss317&include_ext_alt_text=true&include_entities=true&result_type=recent&count=100',
        # 'https://api.twitter.com/1.1/search/tweets.json?q=to%3Az_nxqzi2ksrr9h&include_ext_alt_text=true&include_entities=true&result_type=recent&count=100',
        # 'https://api.twitter.com/1.1/search/tweets.json?q=from%3AReal_Xi_Jinping&include_ext_alt_text=true&include_entities=true&result_type=recent&count=100',
        'https://api.twitter.com/1.1/search/tweets.json?q=from%3Anmslandkiller&include_ext_alt_text=true&include_entities=true&result_type=recent&count=100'

    ]
    custom_settings = {

        "CONCURRENT_REQUESTS": 18,
        "DOWNLOAD_DELAY": 1,
        "COOKIES_ENABLED": True,
        "DOWNLOAD_TIMEOUT": 60

    }

    redis_key = REPLIES_REDIS_KEY

    twitter_apis_key = TWITTER_APIS_KEY

    def __init__(self, *args, **kwargs):
        super(TweSearchRepliesSpider, self).__init__(*args, **kwargs)
        self.db = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_PARAMS["db"],
                                    password=REDIS_PARAMS["password"])
        self.token_db = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_TOKEN_DB,
                                          password=REDIS_PARAMS["password"])

    @staticmethod
    def get_timestamp():
        """获取当前整点时间戳"""
        today = datetime.date.today()
        timeArray = time.strptime(str(today), "%Y-%m-%d")
        timestamp = time.mktime(timeArray)
        return int(timestamp)

    @staticmethod
    def get_current_week():
        """
        获取周一时间戳
        :return:
        """
        monday = datetime.date.today()
        one_day = datetime.timedelta(days=1)
        while monday.weekday() != 0:
            monday -= one_day
        timeArray = time.strptime(str(monday), "%Y-%m-%d")
        timestamp = int(time.mktime(timeArray))
        return timestamp

    def parse(self, response):
        """
        状态码403
        403
        {"errors":[{"code":195,"message":"Missing or invalid url parameter."}]}
        提示用户名不是最新的
        :param response:
        :return:
        """
        if response.status == ERROR_CODE_429:
            self.db.lpush(self.redis_key, response.url)
            return
        if response.status == ERROR_CODE_401:
            token = response.request.meta["token"]
            token = json.dumps(token)
            if response.text:
                dict_res = json.loads(response.text)
                if "errors" in dict_res:
                    self.token_db.zadd(self.twitter_apis_key, MIN_SCORE, token)
                    self.db.lpush(self.redis_key, response.url)
            if not response.text:
                self.db.lpush(self.redis_key, response.url)
            return

        if response.status == ALLOWED_CODE:
            dict_response = json.loads(response.text)
            statuses = dict_response["statuses"]
            for statuse in statuses:
                if "in_reply_to_status_id" in statuse and statuse["in_reply_to_status_id"]:
                    item = Replies()
                    """
                    from user_id 被replies_user_id回复
                    to   user_id 被replies_user_id回复
                    """
                    item["user_id"] = statuse["in_reply_to_user_id_str"]
                    item["user_name"] = statuse["in_reply_to_screen_name"]
                    item["data_id"] = statuse["in_reply_to_status_id_str"]
                    item["replies_user_id"] = statuse["user"]["id_str"]
                    item["replies_user_name"] = statuse["user"]["screen_name"]
                    item["replies_name"] = statuse["user"]["name"]
                    item["replies_text"] = statuse["text"]
                    item["replies_lang"] = statuse["lang"]
                    source_info = re.match(r"<a href=(.*)>(.*)</a>", statuse["source"])
                    item["replies_source"] = source_info.group(2) if source_info else None
                    item["replies_coordinates"] = statuse["coordinates"]
                    item["replies_place"] = statuse["place"]
                    item["replies_status_id"] = statuse["id_str"]
                    item["replies_date_time"] = tweet_time.cst_to_str(statuse["created_at"])
                    item["table"] = REPLIES_TABLE
                    item["storage_date"] = int(time.time())
                    yield item
            if "next_results" in dict_response["search_metadata"]:
                next_url = "https://api.twitter.com/1.1/search/tweets.json" + dict_response["search_metadata"][
                    "next_results"]
                yield scrapy.Request(
                    next_url,
                    callback=self.parse
                )
