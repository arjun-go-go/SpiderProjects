# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TwitterFeedbackItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class Followers(scrapy.Item):
    id = scrapy.Field()
    user_name = scrapy.Field()
    name = scrapy.Field()
    followers_name = scrapy.Field()
    followers_url = scrapy.Field()
    following = scrapy.Field()
    followers_Introduction = scrapy.Field()
    table = scrapy.Field()
    followers_user_id = scrapy.Field()
    followers = scrapy.Field()
    user_id = scrapy.Field()
    location = scrapy.Field()
    join_date = scrapy.Field()
    introduction = scrapy.Field()


class Following(scrapy.Item):
    id = scrapy.Field()
    user_name = scrapy.Field()
    user_id = scrapy.Field()
    own_user_id = scrapy.Field()
    name = scrapy.Field()
    followers_name = scrapy.Field()
    followers_url = scrapy.Field()
    followers_count = scrapy.Field()
    friends_count = scrapy.Field()
    location = scrapy.Field()
    join_date = scrapy.Field()
    introduction = scrapy.Field()
    following = scrapy.Field()
    followers_Introduction = scrapy.Field()
    table = scrapy.Field()
    following_user_id = scrapy.Field()
    followers_user_id = scrapy.Field()
    followers = scrapy.Field()
    storage_date = scrapy.Field()


class Replies(scrapy.Item):

    search_url = scrapy.Field()
    status_url = scrapy.Field()
    tweet_text = scrapy.Field()
    user_name = scrapy.Field()
    user_id = scrapy.Field()
    data_id = scrapy.Field()
    replies_user_name = scrapy.Field()
    replies_user_id = scrapy.Field()
    replies_name = scrapy.Field()
    replies_text = scrapy.Field()
    replies_lang = scrapy.Field()
    replies_source = scrapy.Field()
    replies_coordinates = scrapy.Field()
    replies_place = scrapy.Field()
    replies_date_id = scrapy.Field()
    replies_status_id = scrapy.Field()
    replies_date_time = scrapy.Field()
    replies_url = scrapy.Field()
    table = scrapy.Field()
    storage_date = scrapy.Field()
    res = scrapy.Field()
    next_cursor = scrapy.Field()

class Likes(scrapy.Item):
    user_id = scrapy.Field()
    user_name = scrapy.Field()
    likes_data_id = scrapy.Field()
    likes_data_time = scrapy.Field()
    likes_text = scrapy.Field()
    likes_source = scrapy.Field()
    likes_user_id = scrapy.Field()
    likes_user_name = scrapy.Field()
    likes_name = scrapy.Field()
    likes_user_location = scrapy.Field()
    likes_user_description = scrapy.Field()
    likes_user_followers_count = scrapy.Field()
    likes_user_friends_count = scrapy.Field()
    likes_user_listed_count = scrapy.Field()
    likes_user_favourites_count = scrapy.Field()
    likes_user_statuses_count = scrapy.Field()
    likes_retweet_count = scrapy.Field()
    likes_favorite_count = scrapy.Field()
    likes_lang = scrapy.Field()
    likes_coordinates= scrapy.Field()
    likes_place= scrapy.Field()
    table = scrapy.Field()
    storage_date = scrapy.Field()