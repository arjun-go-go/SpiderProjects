# -*- coding: utf-8 -*-
import redis
import scrapy
import json
import re
from scrapy_redis.spiders import RedisSpider
import time
from ..settings import REDIS_PARAMS, REDIS_HOST, REDIS_PORT
from ..settings import ERROR_CODE_401, ERROR_CODE_429, ERROR_CODE_403, ALLOWED_CODE, ERROR_CODE_404


class TweSpiderMonitorSpider(RedisSpider):
    name = 'twe_spider_monitor'
    allowed_domains = ['twitter.com']
    start_urls = [
        "https://api.twitter.com/1.1/users/show.json?screen_name=MingjingNews",
        "https://api.twitter.com/1.1/users/show.json?screen_name=ntdchinese",
    ]

    custom_settings = {

        'ITEM_PIPELINES': {
            'twitter_search.pipelines.MongoPipeline': 200,
        },
        "CONCURRENT_REQUESTS": 5,
        "DOWNLOAD_DELAY": 2

    }

    redis_key = "twitter_monitor_name"

    def __init__(self, *args, **kwargs):
        super(TweSpiderMonitorSpider, self).__init__(*args, **kwargs)
        self.db = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_PARAMS["db"], password=REDIS_PARAMS["password"])

    def parse(self, response):
        response_code = response.status
        dict_res = json.loads(response.text)
        if "errors" in dict_res and (response_code == ERROR_CODE_429 or response_code == ERROR_CODE_401):
            self.db.lpush(self.redis_key, response.url)
            return
        if "errors" in dict_res and (response_code == ERROR_CODE_404 or response_code == ERROR_CODE_403):
            user_name = re.match(r"https://api\.twitter\.com/1\.1/users/show\.json\?screen_name=(.*)", response.url)
            if user_name:
                print(user_name)
            return
        if response_code == ALLOWED_CODE:
            item = {}
            json_content = json.loads(response.text)
            item["user_id"] = json_content['id_str']
            item["new_name"] = json_content['screen_name']
            item["update_time"] = int(time.time())
            item["status_code"] = 3
            item["lang"] = 0
            item["account_type"] = ""
            yield item
