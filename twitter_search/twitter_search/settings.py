# -*- coding: utf-8 -*-

# Scrapy settings for twitter_search project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'twitter_search'

SPIDER_MODULES = ['twitter_search.spiders']
NEWSPIDER_MODULE = 'twitter_search.spiders'

DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
SCHEDULER_PERSIST = True

REDIS_URL = None
REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
REDIS_PARAMS = {"db": 10, "password": "xxxx"}

REDIS_TOKEN_DB = 2
MIN_SCORE = 2

BLOCK_NUM = 2
BLOOM_FILTER_KEY = "xxxxx_bloom"

MONGO_URI = 'mongodb://Admin:Dev@127.0.0.1:27017/'
MONGO_DATABASE = 'twitter'

LOG_LEVEL = "DEBUG"

# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = 'twitter_search (+http://www.yourdomain.com)'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'

# Obey robots.txts rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 15

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 2
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

DOWNLOAD_TIMEOUT = 30

RETRY_ENABLED = False
# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#
# }

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'twitter_search.middlewares.TwitterSearchSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    # 'twitter_search.middlewares.TwitterSearchDownloaderMiddleware': 543,
    'twitter_search.middlewares.RandomProxyMiddleware': 100,
    'twitter_search.middlewares.TwitterApiMiddleware': 200,
    'twitter_search.middlewares.SpiderMiddleware': 120,

}

MYEXT_ENABLED = True
IDLE_NUMBER = 720

EXTENSIONS = {
    'twitter_search.extensions.RedisSpiderSmartIdleClosedExensions': 500
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    # 'twitter_search.pipelines.MysqlTwistedPipline': 100,
    # 'twitter_search.pipelines.ImgDownloadPipeline': 100,
    # 'twitter_search.pipelines.MongoPipeline': 100,
}

IMAGES_URLS_FIELD = "image_url"
IMAGES_RESULT_FIELD = "image_path"
IMAGES_STORE = './images'

import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'twitter_search'))

RANDOM_UA_TYPE = "random"

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
HTTPERROR_ALLOWED_CODES = [404, 403, 401, 429, 400, 301, 302]

ALLOWED_CODE = 200
ERROR_CODE_429 = 429
ERROR_CODE_401 = 401
ERROR_CODE_403 = 403
ERROR_CODE_404 = 404

TOKEN_URL = "http://127.0.0.1:8880/random"
TOKEN_URL_INIT = "http://127.0.0.1:8881/init"
PROXY_URL = "http://127.0.0.1:1080"
API_URL = "http://127.0.0.1:8881/random"
API_URL_INIT = "http://127.0.0.1:8881/init"

MYSQL_HOST = "127.0.0.1"
MYSQL_DBNAME = 'twitter'
MYSQL_USER = 'user'
MYSQL_PASSWORD = 'pwd'
MYSQL_PORT_1 = 3306

WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=xxxxxx"

