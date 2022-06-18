# -*- coding: utf-8 -*-
import re
import scrapy
import json
from ..items import Likes
from copy import deepcopy
from scrapy_redis.spiders import RedisSpider
import time
import redis
from scrapy.exceptions import CloseSpider
from ..tools.handle_times import tweet_time
from ..settings import REDIS_PARAMS, REDIS_PORT, REDIS_HOST, REDIS_TOKEN_DB, LIKES_TABLE, TWITTER_APIS_KEY, \
    LIKES_REDIS_KEY
from ..settings import ERROR_CODE_401, ERROR_CODE_403, ERROR_CODE_429, ALLOWED_CODE, MIN_SCORE


class TweSpiderLikesSpider(RedisSpider):
    """
    获取点赞信息
    """
    name = 'twe_spider_likes'
    allowed_domains = ['twitter.com']
    start_urls = [
        # 'https://api.twitter.com/1.1/favorites/list.json?count=200&user_id=1181916693234241536',
        # 'https://api.twitter.com/1.1/favorites/list.json?count=200&user_id=1205841262953164802',
        'https://api.twitter.com/1.1/favorites/list.json?count=200&user_id=1247032758230085632',
    ]

    redis_key = LIKES_REDIS_KEY
    twitter_apis_key = TWITTER_APIS_KEY

    def __init__(self, *args, **kwargs):
        super(TweSpiderLikesSpider, self).__init__(*args, **kwargs)
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
        if response.status == ERROR_CODE_401:
            token = response.request.meta["token"]
            token = json.dumps(token)
            dict_res = json.loads(response.text)
            if "errors" in dict_res:
                self.token_db.zadd(self.twitter_apis_key, MIN_SCORE, token)
                self.db.lpush(self.redis_key, response.url)
            return
        if response.status == ALLOWED_CODE:
            response_list = json.loads(response.text)
            max_id = response_list[-1]["id"] - 1 if response_list else None
            item = Likes()
            item["user_id"] = re.findall(r"user_id=(\d+)", response.url)[0]
            for tweet in response_list:
                item["likes_data_id"] = tweet["id_str"]
                item["likes_data_time"] = tweet_time.cst_to_str(tweet["created_at"])
                item["likes_text"] = tweet["text"]
                source_info = re.match(r"<a href=(.*)>(.*)</a>", tweet["source"])
                item["likes_source"] = source_info.group(2) if source_info else None
                item["likes_user_id"] = tweet["user"]["id_str"]
                item["likes_user_name"] = tweet["user"]["screen_name"]
                item["likes_name"] = tweet["user"]["name"]
                item["likes_user_location"] = tweet["user"]["location"]
                item["likes_user_description"] = tweet["user"]["description"]
                item["likes_user_followers_count"] = tweet["user"]["followers_count"]
                item["likes_user_friends_count"] = tweet["user"]["friends_count"]
                item["likes_user_listed_count"] = tweet["user"]["listed_count"]
                item["likes_user_favourites_count"] = tweet["user"]["favourites_count"]
                item["likes_user_statuses_count"] = tweet["user"]["statuses_count"]
                item["likes_retweet_count"] = tweet["retweet_count"]
                item["likes_favorite_count"] = tweet["favorite_count"]
                item["likes_lang"] = tweet["lang"]
                item["likes_coordinates"] = tweet["coordinates"]
                item["likes_place"] = tweet["place"]
                item["storage_date"] = int(time.time())
                item["table"] = LIKES_TABLE
                yield item
            if max_id:
                tweets_next_url = 'https://api.twitter.com/1.1/favorites/list.json?count=200&user_id={}&max_id={}'.format(
                    item["user_id"], max_id)
                yield scrapy.Request(
                    tweets_next_url,
                    callback=self.parse
                )
