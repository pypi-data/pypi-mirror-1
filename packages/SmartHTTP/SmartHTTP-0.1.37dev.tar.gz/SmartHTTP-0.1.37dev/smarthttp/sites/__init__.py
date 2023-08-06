# -*- coding: utf-8 -*-
from smarthttp.client import HTTPClient
import urllib, time
from datetime import datetime
import logging

class SiteFunctionResult(object):
    data = None
    error = True
    error_text = u""
    error_code = 0
    def __init__(self, data=None, error=None, error_text=u"", error_code=0):
        if not data is None and not error:
            self.data = data
            self.error = False
        elif error:
            self.error = True
            self.error_text = error_text
            self.error_code = error_code

    def __repr__(self):
        if type(self.data) == unicode:
            data = self.data.encode('utf-8')
        else:
            data = self.data
        return "<SiteResult(%s, %s)>" % (self.error and ('Error', self.error_text) or ('OK', data))


class HTTPSite(object):
    proto = 'http'
    delay = 0
    last_request = None
    def __init__(self, client=None, log=None, delay=0):
        self.delay = delay
        if not client and not log:
            log = logging.getLogger("smarthttp.sites.%s" % self.__class__.__name__)
        if not client:
            client = HTTPClient(logger=log)
        self.client = client
        if log:
            self.log = log
        elif self.client.log:
            self.log = self.client.log
        else:
            self.log = logging.getLogger(self.__class__.__name__)

    def compile_url(self, url, params=None):
        if params and url:
            for param in params:
                value = params[param]
                if value:
                    if type(value) == unicode:
                        value = value.encode('utf-8')
                    if '?' in url:
                        sp = '&'
                    else:
                        sp = '?'
                    url = "%s%s%s=%s" % (url, sp, param, urllib.quote(value))
        if not '://' in url:
            if url[0] != '/':
                url = "/%s" % url
            if self.base_path:
                url = "%s%s" % (self.base_path, url)
            url = "%s://%s%s" % (self.proto, self.domain, url)
        return url

    def request(self, url, **kw):
        if self.domain:
            url = self.compile_url(url)
        if self.delay and self.last_request:
            td = (datetime.now() - self.last_request).seconds
            if td < self.delay:
                sleep = self.delay - td
                self.log.info("Should sleep %s seconds before next request" % sleep)
                time.sleep(sleep)
        self.last_request = datetime.now()
        req = self.client.request(url, **kw)
        return req

    def error(self, error, code=0):
        return SiteFunctionResult(error=True, error_text=error, error_code=code)

    def error_http(self, request):
        return self.error(u"HTTP request failed, code %s." % request.code, code=request.code)

    def error_html(self, request):
        return self.error(u"Received invalid HTML")

    def error_parse(self, xpath=None):
        return self.error(u"Parse error: xpath=%s" % xpath)
    
    def ok(self, data):
        return SiteFunctionResult(data=data, error=False)

    def result(self, data):
        return SiteFunctionResult(data=data, error=False)

class SpecificSite(HTTPSite):
    pass

class SiteEngine(HTTPSite):
    def __init__(self, client=None, log=None, domain=None, base_path=None, *args, **kw):
        HTTPSite.__init__(self, client=client, log=log, *args, **kw)
        self.domain = domain
        if base_path:
            if base_path[0] != '/':
                base_path = "/%s" % base_path
            if base_path[-1] == '/':
                base_path = base_path[:-1]
        self.base_path = base_path
    
