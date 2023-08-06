# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt


import threading
import urllib2
import time


http_opener = urllib2.OpenerDirector()
for handler in [urllib2.ProxyHandler,
                urllib2.HTTPHandler,
                urllib2.HTTPSHandler,
                urllib2.HTTPDefaultErrorHandler,
                urllib2.HTTPErrorProcessor]:
    http_opener.add_handler(handler())


class URLChecker(threading.Thread):

    min = None
    max = None
    avg = None
    errors = 0
    avg5 = None
    avg100 = None
    code = ''
    checking = False

    def __init__(self, url):
        super(URLChecker, self).__init__()
        self.url = url
        self.history = []
        self.running = True

    def run(self):
        while self.running:
            self.update()
            time.sleep(3)

    @property
    def last(self):
        if self.history:
            return self.history[0]
        return None

    def update(self):
        start = time.time()
        response = None
        request = urllib2.Request(self.url)
        request.add_header('user-agent', 'Bot/httop')
        self.checking = True
        try:
            response = http_opener.open(request)
            code = response.code
        except urllib2.HTTPError, e:
            code = e.code
            response = 'failed' # Satisfy the not None condition further down
        except:
            code = None
            self.errors += 1
        self.checking = False
        end = time.time()
        duration = end-start

        self.code = code

        # Update statistics

        if response is not None:
            self.history.insert(0, duration)
        if self.min is None or duration < self.min:
            self.min = duration
        if self.max is None or duration > self.max:
            self.max = duration
        self.avg = sum(self.history) / len(self.history)
        if len(self.history) >= 5:
            self.avg5 = sum(self.history[:5]) / 5
        if len(self.history) >= 100:
            self.avg100 = sum(self.history[:100]) / 100
