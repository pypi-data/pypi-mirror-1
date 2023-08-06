import sys
import pycurl
from palb.core import URLGetter, Result

if sys.platform == "win32":
    _null_file = 'nul'
else:
    _null_file = '/dev/null'

class PyCurlURLGetter(URLGetter):
    name = 'pycurl'
    fp = open(_null_file, "wb")
    def __init__(self, url_queue, result_queue):
        URLGetter.__init__(self, url_queue, result_queue)
        self.c =  pycurl.Curl()
        self.c.setopt(pycurl.WRITEDATA, self.fp)
        self.c.setopt(pycurl.MAXCONNECTS, 1)
        self.c.setopt(pycurl.FRESH_CONNECT, 1)
    def get_url(self, url):
        self.c.setopt(pycurl.URL, url)
        try:
            self.c.perform()
        except:
            import traceback
            traceback.print_exc()
            return None
        status = self.c.getinfo(pycurl.RESPONSE_CODE)
        size = self.c.getinfo(pycurl.SIZE_DOWNLOAD)
        t_total = self.c.getinfo(pycurl.TOTAL_TIME)
        t_connect = self.c.getinfo(pycurl.CONNECT_TIME)
        t_start = self.c.getinfo(pycurl.STARTTRANSFER_TIME)
        t_proc = t_total - t_connect
        return Result(t_total, size, status, detail_time=(t_connect, t_proc, t_start))

url_getter = PyCurlURLGetter