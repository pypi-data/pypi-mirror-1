# -*- coding: utf-8 -*-
"""
Scraper for hanabira
"""
from smarthttp.sites import SiteEngine
from smarthttp.dom import GetPlainText, GetDOM, ForcedEncoding
import re, datetime
import simplejson

class Hanabira(SiteEngine):
    key = None
    def __init__(self, key=None, **kw):
        SiteEngine.__init__(self, **kw)
        self.key = key

    def get_post_url(self, post, thread, board):
        return self.compile_url("/%s/res/%s.xhtml#i%s" % (board, thread, post))

    def get_post_admin_url(self, post_id):
        return self.compile_url("/admin/get_post/%s" % (post_id))

    def get_new_posts(self, post_id=0, count=10):
        url = "/api/chan/posts/%s/%s" % (post_id, count)
        if self.key:
            url = "%s/%s" % (url, self.key)

        req = self.request(url)
        if req.error or req.code != 200:
            return self.error_http(req)
        posts = simplejson.loads(req.data)
        return self.result(posts)
    
    def hide_post(self, post_id):
        if not self.key:
            return self.error(u"Admin key is needed for hide posts")
        url = '/api/admin/post/hide/%s/%s' % (post_id, self.key)
        req = self.request(url)
        if req.error or req.code != 200:
            return self.error_http(req)
        return self.result(simplejson.loads(req.data))
        
    def show_post(self, post_id):
        if not self.key:
            return self.error(u"Admin key is needed for show posts")
        url = '/api/admin/post/show/%s/%s' % (post_id, self.key)
        req = self.request(url)
        if req.error or req.code != 200:
            return self.error_http(req)
        return self.result(simplejson.loads(req.data))
    
    def ban_user(self, post_id):
        if not self.key:
            return self.error(u"Admin key is needed for ban user")
        url = '/api/admin/user/ban/%s/%s' % (post_id, self.key)
        req = self.request(url)
        if req.error or req.code != 200:
            return self.error_http(req)
        return self.result(simplejson.loads(req.data))
    
    def unban_user(self, post_id):
        if not self.key:
            return self.error(u"Admin key is needed for unban user")
        url = '/api/admin/user/unban/%s/%s' % (post_id, self.key)
        req = self.request(url)
        if req.error or req.code != 200:
            return self.error_http(req)
        return self.result(simplejson.loads(req.data))

    # Should be fixed later
    def parse_local_file(self, fp):
        data = open(fp, 'r').read().decode('utf-8')
        res = []
        document = GetDOM(data)
        posts = document.xpath('/html/body/div')
        for post in posts:
            text = GetPlainText(post)
            res.append(text)
        return self.result(res)        
