from __future__ import division
import sys
import os
import Queue
import threading
import traceback
import itertools

from palb.stats import ResultStats

__version__ = '0.1.0'
__author__ = 'Oliver Tonnhofer <olt@bogosoft.com>'

import signal

keep_processing = True

def stop_processing(_signal, _frame):
    global keep_processing
    print 'STOP'
    keep_processing = False
    return 0

signal.signal(signal.SIGINT, stop_processing)

class Result(object):
    def __init__(self, time, size, status, detail_time=None):
        self.time = time
        self.size = size
        self.status = status
        self.detail_time = detail_time
    
    def __repr__(self):
        return 'Result(%.5f, %d, %d, detail_time=%r)' % (self.time, self.size,
                                                        self.status, self.detail_time)

class URLGetter(threading.Thread):
    def __init__(self, url_queue, result_queue):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.url_queue = url_queue
        self.result_queue = result_queue
    def run(self):
        while keep_processing:
            url = self.url_queue.get()
            if url is None:
                break
            result = self.get_url(url)
            self.result_queue.put(result)
    def get_url(self, url):
        return NotImplementedError

try:
    from palb.getter.curl import url_getter
except ImportError, e:
    from palb.getter.urllib import url_getter

class URLGetterPool(object):
    def __init__(self, size=2):
        self.size = size
        self.url_queue = Queue.Queue(100)
        self.result_queue = Queue.Queue()
        self.getter = []
    def start(self):
        for _ in xrange(self.size):
            t = url_getter(self.url_queue, self.result_queue)
            t.start()
            self.getter.append(t)
    def stop(self):
        for _ in xrange(self.size):
            if not keep_processing:
                break
            self.url_queue.put(None)
        self.getter = []

class URLProducer(threading.Thread):
    def __init__(self, url_queue, urls, n=10):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.url_queue = url_queue
        self.n = n
        if isinstance(urls, basestring):
            urls = itertools.repeat(urls)
        elif isinstance(urls, list):
            urls = itertools.cycle(urls)
        self.url_iter = urls
    
    def run(self):
        for _ in xrange(self.n):
            try:
                self.url_queue.put(self.url_iter.next())
            except StopIteration:
                global keep_processing
                keep_processing = False
                break
    

class PALB(object):
    def __init__(self, urls, c=1, n=1):
        self.c = c
        self.n = n
        self.urls = urls
    def start(self):
        out = sys.stdout
        
        pool = URLGetterPool(self.c)
        pool.start()

        producer = URLProducer(pool.url_queue, self.urls, n=self.n)
        
        print >>out, 'This is palb, Version', __version__
        print >>out, 'Copyright (c) 2009', __author__
        print >>out, 'Licensed under MIT License'
        print >>out
        print >>out, 'Using %s as URL getter.' % url_getter.name 
        print >>out, 'Benchmarking (be patient).....',
        out.flush()
        
        stats = ResultStats()
        producer.start()
        
        for _ in xrange(self.n):
            if not keep_processing:
                break
            stats.add(pool.result_queue.get())
        stats.stop()
        
        print >>out, 'done'
        print >>out
        print >>out
        print >>out, 'Average Document Length: %.0f bytes' % (stats.avg_req_length,)
        print >>out
        print >>out, 'Concurrency Level:    %d' % (self.c,)
        print >>out, 'Time taken for tests: %.3f seconds' % (stats.total_wall_time,)
        print >>out, 'Complete requests:    %d' % (len(stats.results),)
        print >>out, 'Failed requests:      %d' % (stats.failed_requests,)
        print >>out, 'Total transferred:    %d bytes' % (stats.total_req_length,)
        print >>out, 'Requests per second:  %.2f [#/sec] (mean)' % (len(stats.results)/
                                                                    stats.total_wall_time,)
        print >>out, 'Time per request:     %.3f [ms] (mean)' % (stats.avg_req_time*1000,)
        print >>out, 'Time per request:     %.3f [ms] (mean,'\
                     ' across all concurrent requests)' % (stats.avg_req_time*1000/self.c,)
        print >>out, 'Transfer rate:        %.2f [Kbytes/sec] received' % \
                      (stats.total_req_length/stats.total_wall_time/1024,)
        print >>out
        
        connection_times = stats.connection_times()
        if connection_times is not None:
            print >>out, 'Connection Times (ms)'
            print >>out, '              min  mean[+/-sd] median   max'
            names = ('Connect', 'Processing', 'Waiting', 'Total')
            for name, data in zip(names, connection_times):
                t_min, t_mean, t_sd, t_median, t_max = [v*1000 for v in data] # to [ms]
                t_min, t_mean, t_median, t_max = [round(v) for v in t_min, t_mean,
                                                  t_median, t_max]
                print >>out, '%-11s %5d %5d %5.1f %6d %7d' % (name+':', t_min, t_mean, t_sd,
                                                               t_median, t_max)
            print >>out

        print >>out, 'Percentage of the requests served within a certain time (ms)'
        for percent, seconds in stats.distribution():
            print >>out, ' %3d%% %6.0f' % (percent, seconds*1024),
            if percent == 100:
                print >>out, '(longest request)'
            else:
                print >>out
        

def main():
    from optparse import OptionParser
    usage = "usage: %prog [options] url(s)"
    parser = OptionParser(usage=usage, version='%prog ' + __version__)
    parser.add_option('-c', None, dest='c', type='int', default=1,
                      help='number of concurrent requests')
    parser.add_option('-n', None, dest='n', type='int', default=1,
                      help='total number of requests')
    parser.add_option('-u', '--url-func', dest='url_func', default=None,
                      help='''the name of a python function that returns an iterator of
URL strings (package.module:func). the function gets a list with all remaining command
line arguments''')
    parser.add_option('-f', '--url-file', dest='url_file', default=None,
                      help='''file with one URL per line''')
    
    (options, args) = parser.parse_args()
    
    if options.url_file is not None:
        if options.url_file == '-':
            urls = [line.strip() for line in sys.stdin]
        else:
            urls = [line.strip() for line in open(options.url_file)]
    elif options.url_func is not None:
        module, func = options.url_func.split(':')
        module = __import__(module)
        urls = getattr(module, func)(args)
    elif len(args) > 0:
        urls = args
    else:
        parser.error('need one or more URL(s) or -u|-f argument')
    palb = PALB(urls, c=options.c, n=options.n)
    palb.start()
