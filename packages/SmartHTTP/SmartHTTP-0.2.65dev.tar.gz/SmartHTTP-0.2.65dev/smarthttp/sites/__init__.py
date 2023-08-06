# -*- coding: utf-8 -*-
from smarthttp.client import HTTPClient
import urllib, time
from urlparse import urlparse
from datetime import datetime
from decorator import decorator
from .exceptions import ParseException, XPathException, HTTPException, HTMLException
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

    def __bool__(self):
        return not self.error
    def __nonzero__(self):
        return not self.error

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
    base_path = None
    domain = None
    def __init__(self, client=None, log=None, delay=0, **kw):
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
                    elif type(value) != str:
                        value = str(value)
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


    def assertHTTPOK(self, request):
        if request.error:
            raise HTTPException(u"HTTP Error")
        if request.code != 200:
            raise HTTPException(u"HTTP code %s" % request.code)
        return True

    def assertHTML(self, request):
        self.assertHTTPOK(request)
        document = request.dom
        return document

    def assertJSON(self, request):
        self.assertHTTPOK(request)
        document = request.json
        return document
        
    def assertXPath(self, node, path, count=1, strict=False):
        res = node.xpath(path)
        if not res:
            raise XPathException(u"{0} did not match anything.".format(path))
        elif strict and len(res) != count:
            raise XPathException(u"{0} matched {1} instead of {2}.".format(path, len(res), count))
        elif not strict and len(res) < count:
            raise XPathException(u"{0} matched {1} which is less than {2}.".format(path, len(res), count))
        return res
        
    def assertXPathOne(self, node, path):
        res = self.assertXPath(node, path, 1, True)
        return res[0]


    def __repr__(self):
        return "<Site[{0.__class__.__name__}] @ {0.proto} {0.domain} {0.base_path}>".format(self)

class SpecificSite(HTTPSite):
    pass

class SiteEngine(HTTPSite):
    def __init__(self, client=None, log=None, domain=None, base_path=None, url=None, *args, **kw):
        HTTPSite.__init__(self, client=client, log=log, *args, **kw)
        if url:
            urlp = urlparse(url)
            domain = urlp.hostname or domain
            base_path = urlp.path or base_path
        self.domain = domain
        if base_path:
            if base_path[0] != '/':
                base_path = "/%s" % base_path
            if base_path[-1] == '/':
                base_path = base_path[:-1]
        self.base_path = base_path

@decorator    
def parser(func, self, *args, **kw):
    """
    This decorator will catch parsing exceptions and gracefully return site.error()
    """
    try:
        return func(self, *args, **kw)
    except ParseException, e:
        return self.error(str(e))
