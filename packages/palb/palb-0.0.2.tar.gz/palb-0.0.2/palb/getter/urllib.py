import os
import urllib2
import time
from palb.core import URLGetter, Result

# urllib2 does some lazy loading. so we do a dummy request here to get more
# acurate results for the first request
_prime_url = 'file://'+os.path.abspath(__file__)
urllib2.urlopen(_prime_url).read()

class URLLibURLGetter(URLGetter):
    name = 'urllib'
    def __init__(self, url_queue, result_queue):
        URLGetter.__init__(self, url_queue, result_queue)
        self.opener = urllib2.build_opener()
    def get_url(self, url):
        start = time.time()
        size = status = 0
        try:
            result = self.opener.open(url)
            size = len(result.read())
            status = result.code
        except urllib2.HTTPError, e:
            size = len(e.read())
            status = e.code
        except:
            import traceback
            traceback.print_exc()
            return None
        total_time = time.time() - start
        return Result(total_time, size, status)

url_getter = URLLibURLGetter