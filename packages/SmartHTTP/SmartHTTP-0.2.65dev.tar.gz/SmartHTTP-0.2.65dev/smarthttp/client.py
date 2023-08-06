# -*- coding: utf-8 -*-
import os, random
import logging
from curl import DoHTTPRequest
log = logging.getLogger(__name__)

user_agents = open(os.path.join(os.path.dirname(__file__), 'ua.txt')).read().split('\n')

class HTTPClient(object):
    def __init__(self, thread=None, logger=None, ua=None):
        global log
        self.thread = thread
        if logger:
            self.log = logger
        elif self.thread:
            self.log = logging.getLogger("%s.client" % (thread.name))
        else:
            self.log = logging.getLogger(__name__)
        self.cookies = {}
        if ua:
            self.user_agent = ua
        else:
            self.user_agent = random.choice(user_agents)
        self.history = []

    def load(self, site):
        site.load(self)

    def request(self, url, data=None, referer=None, request="GET", retry=5, timeout=120):
        if not referer:
            if self.history:
                referer = self.history[-1]['url']
            else:
                referer = url
        attempt = 1
        while attempt < retry:
            if self.thread:
                self.thread.check_kill()
            reply = DoHTTPRequest(url, data=data, referer=referer, request=request, cookies=self.cookies, user_agent=self.user_agent, logger=self.log, timeout=timeout)
            if self.thread:
                self.thread.check_kill()
            if reply.error:
                self.log.debug("Attempt %s failed for url %s" % (attempt, url))
                attempt += 1
            else:
                break
        self.cookies = reply.cookies
        self.history.append({'url':url})
        return reply
