# -*- coding: utf-8 -*-

from pycurl import *
from lxml import etree
import StringIO
import demjson as json
import logging
log = logging.getLogger(__name__)

class HTTPResult:
    html_parser = etree.HTMLParser()
    def __init__(self, c, data, headers, cookies=None):
        self.error = False
        self.data = data
        self.header = headers
        self.document = None
        headers = headers.split("\r\n")
        self.date = c.getinfo(INFO_FILETIME)
        self.code = c.getinfo(HTTP_CODE)
        self.size = c.getinfo(CONTENT_LENGTH_DOWNLOAD)
        self.url  = c.getinfo(EFFECTIVE_URL)
        self.headers = {}
        self.cookies = cookies or {}
        for h in headers:
            s = h.split(":", 1)
            if s[0].lower() == 'set-cookie':
                cookie_parts = s[1].strip().split(';')
                cookie = cookie_parts[0].split('=', 1)
                self.cookies[cookie[0]] = cookie[1]
            else:
                self.headers[s[0].lower()] = len(s) > 1 and s[1].strip() or ''
        if self.headers.get("content-type",False):
            type = self.headers['content-type'].split("/")
            self.type = type[0]
            self.subtype = len(type) > 1 and type[1] or ''
        else:
            self.type = "text"
            self.subtype = "plain"

    @property
    def json(self):
        if self.document:
            return self.document
        elif self.data:
            self.document = json.decode(self.data)
            return self.document
        else:
            return None
            
    @property
    def xml(self):
        if self.document:
            return self.document
        elif self.data:
            self.document = etree.fromstring(self.data)
            return self.document
        else:
            return None

    @property
    def dom(self):
        if self.document:
            return self.document
        elif self.data:
            self.document = etree.parse(StringIO.StringIO(self.data), self.html_parser)
            return self.document
        else:
            return None

class HTTPError(HTTPResult):
    def __init__(self, c, e):
        self.data = None
        self.cookies = None
        self.headers = None
        self.document = None
        self.type = None
        self.subtype = None
        self.error = True
        self.error_text = e
        self.date = c.getinfo(INFO_FILETIME)
        self.code = c.getinfo(HTTP_CODE)
        self.size = c.getinfo(CONTENT_LENGTH_DOWNLOAD)
        self.url  = c.getinfo(EFFECTIVE_URL)        
        
    
def DoHTTPRequest(uri, referer=None, cookies=None, request="GET", data=[], connecttimeout=30, timeout=120, signals=False, logger=None, verbose=True,
        user_agent="Mozilla/5.0 (Windows; U; Windows NT 5.1; ru; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3",
        ):
    if not logger:
        logger = log
    c = Curl()
    d = StringIO.StringIO()
    h = StringIO.StringIO()
    c.setopt(URL, str(uri))
    if data:
        if type(data) == dict:
            data_list = []
            for k in data:
                data_list.append((k, data[k]))
        else:
            data_list = data
        c.setopt(POST, 1)
        c.setopt(HTTPPOST, data_list)
        request = "POST"
    elif request == "GET":
        c.setopt(HTTPGET, 1)
    elif request == "HEAD":
        c.setopt(NOBODY, 1)
    else:
        c.setopt(POST, 1)
    c.setopt(WRITEFUNCTION, d.write)
    c.setopt(HEADERFUNCTION, h.write)
    c.setopt(CONNECTTIMEOUT, connecttimeout)
    c.setopt(TIMEOUT, timeout)
    c.setopt(OPT_FILETIME, 1)
    c.setopt(ENCODING, "")
    c.setopt(FOLLOWLOCATION, 0)
    if not signals:
        c.setopt(NOSIGNAL, 1)
    if referer:
        c.setopt(REFERER, str(referer))
    else:
        c.setopt(REFERER, str(uri))
    cookie_str = ""
    if cookies:
        for k in cookies:
            cookie_str += "%s=%s; " % (k, cookies[k])
    c.setopt(COOKIE, str(cookie_str))
    c.setopt(USERAGENT, str(user_agent))
    if verbose:
        logger.debug("%s %s, data %s, cookies %s" % (request, uri, data, cookies))
    else:
        logger.debug("%s %s" % (request, uri))
    try:
        c.perform()
        r = HTTPResult(c, d.getvalue(), h.getvalue(), cookies)
        logger.debug("Finished, code %s, %s bytes" % (r.code, len(r.data)))
    except Exception, e:
        logger.warn(e)
        r = HTTPError(c, e)
    c.close()
    return r

