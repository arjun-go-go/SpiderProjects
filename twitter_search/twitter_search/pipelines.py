# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import datetime
import time
import pymongo
import pymysql
from py2neo import Graph, Node, Relationship
from twisted.enterprise import adbapi
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
import scrapy
import redis
from .settings import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DBNAME, REDIS_PARAMS
from .settings import REDIS_HOST, REDIS_PORT
from .bot import Ding_Bot
from .settings import MONGO_DATABASE, MONGO_URI, BLOCK_NUM, BLOOM_FILTER_KEY


class TwitterSearchPipeline(object):
    def process_item(self, item, spider):
        return item



class MysqlTwistedPipline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            port=settings["MYSQL_PORT"],
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool("pymysql", **dbparms)
        return cls(dbpool)

    def process_item(self, item, spider):
        if spider.name == "twe_spider_id":
            query = self.dbpool.runInteraction(self.do_insert, item)
            query.addErrback(self.handle_error, item, spider)
        else:
            query = self.dbpool.runInteraction(self.do_insert, item)
            query.addErrback(self.handle_error, item, spider)

    def handle_error(self, failure, item, spider):
        print(failure)

    def do_insert(self, cursor, item):
        insert_sql, params = item.get_insert_sql()
        cursor.execute(insert_sql, params)


class Neo4jPipline(object):

    def __init__(self):
        self.graph = Graph("http://127.0.0.1:7474", username="neo4j", password="123456789")

    def process_item(self, item, spider):
        tx = self.graph.begin()
        worker_list = [{"name": item["username"]}, {"name": item["following"]}]
        for worker in worker_list:
            node = Node("Person", **worker)
            tx.merge(node)
        node_1 = Node(name=item["username"])
        node_2 = Node(name=item["following"])
        rel = Relationship(node_1, "following", node_2)
        try:
            tx.merge(rel)
            print("successful")
            tx.commit()
        except Exception as e:
            print(e)
            print("Failed")


class MongoPipeline(object):

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI', MONGO_URI),
            mongo_db=crawler.settings.get('MONGO_DATABASE', MONGO_DATABASE)
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[item['table']].insert_one(dict(item))
        return item


class ImgDownloadPipeline(ImagesPipeline):

    def file_path(self, request, response=None, info=None):
        url = request.url
        file_name = url.split('/')[-1]
        return file_name

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem('Image Downloaded Failed')
        item['image_path'] = image_paths[0]
        return item

    def get_media_requests(self, item, info):
        yield scrapy.Request(item['image_url'])


class RedisPipeline(object):
    def __init__(self):
        self.db_conn = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=15)

    def close_spider(self, spider):
        self.db_conn.connection_pool.disconnect()

    def process_item(self, item, spider):
        self.db_conn.lpush('twitter_monitor', 'https://twitter.com/@{0}'.format(item["new_name"]))
        return item


class SimpleHash(object):
    def __init__(self, cap, seed):
        self.cap = cap
        self.seed = seed

    def hash(self, value):
        ret = 0
        for i in range(len(value)):
            ret += self.seed * ret + ord(value[i])
        return (self.cap - 1) & ret


class BloomFilter(object):
    def __init__(self, server, key, blockNum=2):
        """Redis的String类型最大容量为512M，现使用256M"""
        self.bit_size = 1 << 31
        self.seeds = [5, 7, 11, 13, 31, 37, 61]
        self.server = server
        self.key = key
        self.blockNum = blockNum
        self.hashfunc = []
        for seed in self.seeds:
            self.hashfunc.append(SimpleHash(self.bit_size, seed))

    def isContains(self, str_input):
        if not str_input:
            return False
        ret = True

        name = self.key + str(int(str_input[0:2], 16) % self.blockNum)
        for f in self.hashfunc:
            loc = f.hash(str_input)
            ret = ret & self.server.getbit(name, loc)
        return ret

    def insert(self, str_input):
        name = self.key + str(int(str_input[0:2], 16) % self.blockNum)
        for f in self.hashfunc:
            loc = f.hash(str_input)
            self.server.setbit(name, loc, 1)


class MongoPipelineHours(object):

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.server = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_PARAMS["db"],
                                        password=REDIS_PARAMS["password"])
        self.key = BLOOM_FILTER_KEY
        self.bf = BloomFilter(self.server, self.key, blockNum=BLOCK_NUM)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI', MONGO_URI),
            mongo_db=crawler.settings.get('MONGO_DATABASE', MONGO_DATABASE)
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def users_filter(self, item):
        if item["retweeted_times"]:
            return item["user_id"] + item["data_id"] + str(item["retweeted_times"])
        return item["user_id"] + item["data_id"] + str(item["data_time"])

    def bloom_filter(self, value):
        if self.bf.isContains(value):
            return True
        else:
            self.bf.insert(value)
            return False

    def process_item(self, item, spider):
        value = self.users_filter(item)
        if not self.bloom_filter(value):
            self.db[item['table']].insert_one(dict(item))
            return item
