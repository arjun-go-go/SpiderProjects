# -*- coding: utf-8 -*-
import scrapy
import json
import re
import redis
import scrapy
from scrapy.exceptions import CloseSpider
from ..tools.handle_times import tweet_time
from ..items import Following, Followers
from scrapy_redis.spiders import RedisSpider
from ..settings import REDIS_HOST, REDIS_PARAMS, REDIS_PORT, REDIS_TOKEN_DB, MIN_SCORE, FOLLOWERS_TABLE, \
    TWITTER_APIS_KEY, FOLLOWERS_REDIS_KEY
from ..settings import ERROR_CODE_404, ERROR_CODE_401, ERROR_CODE_403, ERROR_CODE_429, ALLOWED_CODE
from copy import deepcopy
from scrapy_redis.utils import bytes_to_str
from scrapy.http import Request


class TweSpiderFollowersSpider(RedisSpider):
    name = 'twe_spider_followers'
    allowed_domains = ['twitter.com']

    start_urls = [
        # "https://api.twitter.com/1.1/followers/list.json?cursor=-1&user_id=3223940743&count=200&skip_status=true&include_user_entities=false",
        "https://api.twitter.com/1.1/followers/list.json?cursor=-1&user_id=211904023&count=200&skip_status=true&include_user_entities=false"
    ]

    redis_key = FOLLOWERS_REDIS_KEY
    twitter_apis_key = TWITTER_APIS_KEY

    def __init__(self, *args, **kwargs):
        super(TweSpiderFollowersSpider, self).__init__(*args, **kwargs)
        self.db = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_PARAMS["db"],
                                    password=REDIS_PARAMS["password"])
        self.token_db = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_TOKEN_DB,
                                          password=REDIS_PARAMS["password"])

    def parse(self, response):
        if response.request.meta["token"] == "limit":
            self.db.lpush(self.redis_key, response.url)
            raise CloseSpider('CloseSpider_: {}'.format("Rate limit exceeded or ApiPool limit exceeded"))
        if response.status == ERROR_CODE_429:
            self.db.lpush(self.redis_key, response.url)
            return
        if response.status == ERROR_CODE_403 or response.status == ERROR_CODE_401:
            """
            401 {"request":"\/1.1\/statuses\/user_timeline.json","error":"Not authorized."}
            账号被冻结情况

            401 response 为空 原因未知
            """
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
            followers_item = Following()
            followers_item["own_user_id"] = re.match(r".*user_id=(\d+).*", response.url).group(1)
            dict_response = json.loads(response.text)
            users_list = dict_response["users"]
            for users in users_list:
                followers_item["user_name"] = users["screen_name"]
                followers_item["user_id"] = users["id_str"]
                followers_item["name"] = users["name"]
                followers_item["table"] = FOLLOWERS_TABLE
                yield followers_item

            next_cursor = dict_response["next_cursor"]
            if next_cursor != 0:
                next_url = 'https://api.twitter.com/1.1/followers/list.json?cursor={}&user_id={}&count=200&skip_status=true&include_user_entities=false'.format(
                    next_cursor, followers_item["own_user_id"])
                yield scrapy.Request(next_url,
                                     callback=self.parse
                                     )
