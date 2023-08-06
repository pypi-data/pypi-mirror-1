from __future__ import with_statement
from Queue import Queue
from tests.http import mock_httpd
from nose.tools import *

from palb.getter.pycurl import url_getter

SERVER = ('127.0.0.1', 24432)

class TestPyCurlURLGetter(object):
    def setup(self):
        self.url_queue = Queue()
        self.result_queue = Queue()
        self.g = url_getter(self.url_queue, self.result_queue)
        self.g.start()
    def test_single_get(self):
        req = ({'path': r'/foo'},{'body': '12345'})
        with mock_httpd(SERVER, [req]):
            self.url_queue.put('http://%s:%d/foo' % SERVER)
            result = self.result_queue.get()
            eq_(result.size, 5)
            eq_(result.status, 200)
    def test_multi_get(self):
        req1 = ({'path': r'/foo'},{'body': '12345'})
        req2 = ({'path': r'/bar'},{'body': '1234567', 'status': 404})
        with mock_httpd(SERVER, [req1, req2]):
            self.url_queue.put('http://%s:%d/foo' % SERVER)
            self.url_queue.put('http://%s:%d/bar' % SERVER)
            result = self.result_queue.get()
            eq_(result.size, 5)
            eq_(result.status, 200)
            assert_almost_equal(result.time, 0, 1)
            assert_almost_equal(result.detail_time[0], 0, 2)
            assert result.time > result.detail_time[1] > result.detail_time[0]
            result = self.result_queue.get()
            eq_(result.size, 7)
            eq_(result.status, 404)
            assert_almost_equal(result.time, 0, 1)
            assert_almost_equal(result.detail_time[0], 0, 2)
            assert result.time > result.detail_time[1] > result.detail_time[0]
