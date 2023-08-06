from unittest import TestCase

from scrapy.http import Response, Request
from scrapy.spider import BaseSpider
from scrapy.contrib.spidermiddleware.httperror import HttpErrorMiddleware


class TestHttpErrorMiddleware(TestCase):

    def setUp(self):
        self.spider = BaseSpider()
        self.mw = HttpErrorMiddleware()
        self.req = Request('http://scrapytest.org')

        self.res200 = Response('http://scrapytest.org', status=200)
        self.res200.request = self.req
        self.res404 = Response('http://scrapytest.org', status=404)
        self.res404.request = self.req

    def test_process_spider_input(self):
        self.assertEquals(self.mw.process_spider_input(self.res200, self.spider),
                          None)

        self.assertEquals(self.mw.process_spider_input(self.res404, self.spider),
                          [])

    def test_handle_httpstatus_list(self):
        res = self.res404.copy()
        res.request = Request('http://scrapytest.org',
                              meta={'handle_httpstatus_list': [404]})

        self.assertEquals(self.mw.process_spider_input(res, self.spider),
                          None)

        self.spider.handle_httpstatus_list = [404]
        self.assertEquals(self.mw.process_spider_input(self.res404, self.spider),
                          None)

