# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import random
import time
import json
import requests
from dingtalkchatbot.chatbot import DingtalkChatbot
from fake_useragent import UserAgent
from scrapy import signals
from oauthlib.oauth1 import Client as Oauth1Client
from .settings import API_URL, PROXY_URL
from twisted.internet.error import TimeoutError, TCPTimedOutError, \
    ConnectionRefusedError, DNSLookupError, ConnectionLost, ConnectError
from twisted.web._newclient import ResponseNeverReceived
from scrapy.core.downloader.handlers.http11 import TunnelError
from scrapy.spidermiddlewares.httperror import HttpError
import socket


class TwitterSearchSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class TwitterSearchDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class SpiderMiddleware(object):
    def __init__(self):
        self.WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxx"
        self.Ding_Bot = DingtalkChatbot(self.WEBHOOK)

    def get_host_ip(self):

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()

        return ip

    def process_exception(self, request, exception, spider):
        if isinstance(exception, (TimeoutError, TCPTimedOutError,
                                  ConnectionRefusedError,
                                  ResponseNeverReceived, TunnelError,
                                  HttpError, DNSLookupError,
                                  ConnectionLost, ConnectError
                                  )):
            self.Ding_Bot.send_text("""ip_{}_spiders_{}_{}""".format(self.get_host_ip(), spider.name, str(exception)))
            return request


class RandomUserAgentMiddlware(object):
    def __init__(self, crawler):
        super(RandomUserAgentMiddlware, self).__init__()
        self.ua = UserAgent(use_cache_server=False)
        self.ua_type = crawler.settings.get("RANDOM_UA_TYPE", "random")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        def get_ua():
            return getattr(self.ua, self.ua_type)

        request.headers.setdefault('User-Agent', get_ua())


class RandomProxyMiddleware(object):
    def process_request(self, request, spider):
        spider.logger.info("subtitleSpiderMiddleware process_request: request=%s, spider=%s", request, spider)

        request.meta["proxy"] = PROXY_URL


class TwitterApiMiddleware(object):

    def __init__(self):
        self.token_url = API_URL

    def get_random_token(self):
        try:
            response = requests.get(self.token_url)
            if response.status_code == 200:
                token_str = response.text
                return token_str
        except requests.ConnectionError:
            return False

    def process_request(self, request, spider):
        if "api" in request.url:
            tokens = self.get_random_token()
            if tokens != "api limit":
                token = json.loads(tokens)
                """
                    {
                    "access_token": "2474326578-9qWvD4oVAxGcHJ5rQqSNjlD5ilSkDjBvwc6hPtS",
                    "access_token_secret": "FTPBcxgr5hxwcZ8O8J6eN2L8tvOTzvzSjMqcfrZdgj9u3",
                    "consumer_key": "p0xUdkuEaTOOw2maptTWLJ2bC",
                    "consumer_secret": "RBHC9dDcbtMGCs9RFIE9ZOGqpngjeCP02WOho40Wy61uLb7dts"
                     }
                """
                auth = Oauth1Client(
                    client_key=token['consumer_key'],
                    client_secret=token['consumer_secret'],
                    resource_owner_key=token['access_token'],
                    resource_owner_secret=token['access_token_secret'])

                uri, headers, body = auth.sign(request.url)
                request.headers['Authorization'] = [headers['Authorization']]
                request.meta['oauth'] = True
                request.meta['token'] = token
            else:
                request.meta['oauth'] = False
                request.meta['token'] = "limit"

        else:
            return None
