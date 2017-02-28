# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
import logging

from pusher import Pusher
from scrapy import Request
from scrapy.conf import settings
from scrapy.exceptions import DropItem
from urllib.parse import quote
from hashlib import md5
from bson.objectid import ObjectId


class ScrapperPipeline(object):
    def process_item(self, item, spider):
        return item


class ScreenshotPipeline(object):
    """Pipeline that uses Splash to render screenshot of
    every Scrapy item."""

    SPLASH_URL = settings['SPLASH_URL']

    def process_item(self, item, spider):
        print("In process_item url = ", item["url"])
        encoded_item_url = quote(item["url"])
        screenshot_url = self.SPLASH_URL.format(encoded_item_url)
        request = Request(screenshot_url)
        dfd = spider.crawler.engine.download(request, spider)
        dfd.addBoth(self.return_item, item)
        return dfd

    @staticmethod
    def return_item(response, item):
        if response.status != 200:
            # Error happened, return item.
            return item

        # Save screenshot to file, filename will be hash of url.
        url = item["url"]
        url_hash = md5(url.encode("utf8")).hexdigest()
        filename = "{}.png".format(url_hash)
        with open(filename, "wb") as f:
            f.write(response.body)

        # Store filename in item.
        item["screenshot_filename"] = filename
        return item


class MongoDBPipeline(object):

    def __init__(self):
        connection = pymongo.MongoClient(
            settings['MONGODB_HOST'],
            settings['MONGODB_PORT']
        )
        db = connection[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]

        if settings['PUSHER_ENABLED']:
            self.pusher = Pusher(
                app_id=settings['PUSHER_APP_ID'],
                key=settings['PUSHER_KEY'],
                secret=settings['PUSHER_SECRET'],
                ssl=True
            )

    def process_item(self, item, spider):
        for data in item:
            if not data:
                raise DropItem('Missing data!')

        doc = self.collection.find_one({'url': item['url']})
        if doc == None:
            #self.collection.update({'url': item['url']}, dict(item), upsert=True)
            doc = {
                'url': item['url'],
                'title': item['title'],
                'status': item['status'],
                'crawled': item['crawled']
            }
            #html = response.body[:1024 * 256]
            self.collection.insert_one(doc)
            logging.debug("New document in MongoDB: %s" % doc['url'])

            if settings['PUSHER_ENABLED']:
                self.pusher.trigger('urls', 'new_url', {
                    'id': str(ObjectId(doc['_id'])),
                    'url': doc['url'],
                    'crawled': doc['crawled']
                })

        return item
