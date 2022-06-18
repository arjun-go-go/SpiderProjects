# -*- coding: utf-8 -*-
import json
import redis
import scrapy
from scrapy.exceptions import CloseSpider
from ..items import Profile, Tweet
from copy import deepcopy
from ..tools.handle_times import tweet_time
import re, time
from scrapy_redis.spiders import RedisSpider
from ..settings import REDIS_HOST, REDIS_PORT, REDIS_PARAMS, REDIS_TOKEN_DB, MIN_SCORE
from ..settings import ERROR_CODE_401, ERROR_CODE_429, ERROR_CODE_403, ALLOWED_CODE


class TweNewMonitorSpider(RedisSpider):
    name = 'twe_new_monitor'
    allowed_domains = ['twitter.com']
    start_urls = [
        "https://api.twitter.com/1.1/users/show.json?user_id=363414953",
        "https://api.twitter.com/1.1/users/show.json?user_id=396819356"
    ]

    custom_settings = {
        'ITEM_PIPELINES': {
            'twitter_search.pipelines.MongoPipeline': 200

        },
        "CONCURRENT_REQUESTS": 5,
        "DOWNLOAD_DELAY": 2
    }

    redis_key = "twitter_monitor"
    twitter_apis_key = "twitter_apis"

    def __init__(self, *args, **kwargs):
        super(TweNewMonitorSpider, self).__init__(*args, **kwargs)
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
            response_dict = json.loads(response.text)
            user_item = Profile()
            user_item["user_name"] = response_dict["screen_name"]
            user_item["user_id"] = response_dict["id_str"]
            user_item["name"] = response_dict["name"]
            user_item["following"] = response_dict["friends_count"]
            user_item["followers"] = response_dict["followers_count"]
            user_item["location"] = response_dict["location"]
            user_item["join_date"] = tweet_time.cst_to_time(response_dict["created_at"]) - 8 * 60 * 60
            user_item["introduction"] = response_dict["description"]
            user_item["badges"] = response_dict["verified"]
            user_item["protected"] = response_dict["protected"]
            user_item['storage_date'] = int(time.time())
            user_item["table"] = 'users_monitor'
            yield user_item

            next_url = 'https://api.twitter.com/1.1/statuses/user_timeline.json?user_id={}&count=200&exclude_replies=true'.format(
                user_item["user_id"])
            yield scrapy.Request(next_url,
                                 callback=self.parse_tweets,
                                 meta={"item": deepcopy(user_item)})

    def parse_tweets(self, response):
        user_item = deepcopy(response.meta["item"])
        if response.status == ALLOWED_CODE:
            list_response = json.loads(response.text)
            max_id = list_response[-1]["id"] - 1 if list_response else None
            for tweets in list_response:
                item = Tweet()
                item["user_id"] = tweets["user"]["id_str"]
                item["name"] = tweets["user"]["name"]
                item["user_name"] = tweets["user"]["screen_name"]
                item["tweet_text"] = tweet_time.strip_str(tweets["text"])
                item["lang"] = tweets["lang"]
                source_info = re.match(r"<a href=(.*)>(.*)</a>", tweets["source"])
                item["source"] = source_info.group(2) if source_info else None
                item["replies"] = 0
                item["coordinates"] = tweets["coordinates"]
                item["place"] = tweets["place"]
                if "extended_entities" in tweets:
                    item["media_images"] = []
                    for media in tweets["extended_entities"]["media"]:
                        media_dict = {}
                        media_dict["media_status_id"] = media["id_str"]
                        media_dict["media_url"] = media["media_url_https"]
                        item["media_images"].append(media_dict)

                if tweets["entities"]["urls"]:
                    item["data_expanded_url"] = []
                    for url in tweets["entities"]["urls"]:
                        item["data_expanded_url"].append(url["expanded_url"])

                if tweets["entities"]["hashtags"]:
                    item["hashtags"] = tweets["entities"]["hashtags"]

                if tweets["entities"]["user_mentions"]:
                    item["tweet_list"] = tweets["entities"]["user_mentions"]

                if "quoted_status" in tweets:
                    item["quoted_status_id"] = tweets["quoted_status_id_str"]
                    item["quoted_user_id"] = tweets["quoted_status"]["user"]["id_str"]
                    item["quoted_user_name"] = tweets["quoted_status"]["user"]["screen_name"]

                item["data_time"] = tweet_time.cst_to_time(tweets["created_at"])
                item["retweeted_times"] = None
                item["tweet_name"] = item["user_name"]
                item["tweet_id"] = item["user_id"]
                item["data_id"] = tweets["id_str"]
                item["retweets"] = tweets["retweet_count"]
                item["favorites"] = tweets["favorite_count"]
                item["data_retweeter"] = None
                item["data_retweet_id"] = None
                item["url"] = "https://twitter.com/{}/status/{}".format(item["tweet_name"], item["data_id"])

                if "retweeted_status" in tweets:
                    item["data_time"] = tweet_time.cst_to_time(tweets["retweeted_status"]["created_at"])
                    item["retweeted_times"] = tweet_time.cst_to_time(tweets["created_at"])
                    item["tweet_name"] = tweets["retweeted_status"]["user"]["screen_name"]
                    item["tweet_id"] = tweets["retweeted_status"]["user"]["id_str"]
                    item["data_id"] = tweets["retweeted_status"]["id_str"]
                    item["retweets"] = tweets["retweeted_status"]["retweet_count"]
                    item["favorites"] = tweets["retweeted_status"]["favorite_count"]
                    item["data_retweeter"] = item["user_id"]
                    item["data_retweet_id"] = tweets["id_str"]
                    """https://twitter.com/mranti/status/1223412626509594625"""
                    item["url"] = "https://twitter.com/{}/status/{}".format(item["tweet_name"], item["data_id"])

                item['storage_date'] = int(time.time())

                item["table"] = 'tweets_monitor'
                yield item

            tweets_next_url = 'https://api.twitter.com/1.1/statuses/user_timeline.json?user_id={}&count=200&exclude_replies=true&max_id={}'.format(
                user_item["user_id"], max_id)
            yield scrapy.Request(tweets_next_url,
                                 callback=self.parse_tweets,
                                 meta={"item": deepcopy(user_item)})
