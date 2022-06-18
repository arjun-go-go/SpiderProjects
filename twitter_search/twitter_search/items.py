# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Item(scrapy.Item):
    table = scrapy.Field()


class Profile(Item):
    name = scrapy.Field()
    user_name = scrapy.Field()
    user_id = scrapy.Field()
    tweets = scrapy.Field()
    following = scrapy.Field()
    followers = scrapy.Field()
    location = scrapy.Field()
    favorites = scrapy.Field()
    join_date = scrapy.Field()
    introduction = scrapy.Field()
    point = scrapy.Field()
    badges = scrapy.Field()
    protected = scrapy.Field()
    storage_date = scrapy.Field()


class Tweet(scrapy.Item):
    name = scrapy.Field()
    user_id = scrapy.Field()
    user_name = scrapy.Field()
    tweet_list = scrapy.Field()
    tweet_name = scrapy.Field()
    tweet_id = scrapy.Field()
    tweet_text = scrapy.Field()
    replies = scrapy.Field()
    retweets = scrapy.Field()
    favorites = scrapy.Field()
    data_time = scrapy.Field()
    data_id = scrapy.Field()
    media_images = scrapy.Field()
    media_status_id = scrapy.Field()
    url = scrapy.Field()
    data_retweeter = scrapy.Field()
    data_retweet_id = scrapy.Field()
    data_expanded_url = scrapy.Field()
    retweeted_times = scrapy.Field()
    lang = scrapy.Field()
    expanded_domain = scrapy.Field()
    place = scrapy.Field()
    coordinates = scrapy.Field()
    source = scrapy.Field()
    hashtags = scrapy.Field()
    quoted_status_id = scrapy.Field()
    quoted_user_id = scrapy.Field()
    quoted_user_name = scrapy.Field()
    table = scrapy.Field()
    storage_date = scrapy.Field()
    tweet_type = scrapy.Field()
