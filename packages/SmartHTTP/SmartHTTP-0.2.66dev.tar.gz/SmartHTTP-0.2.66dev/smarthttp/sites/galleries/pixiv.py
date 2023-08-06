# -*- coding: utf-8 -*-
"""
Client for www.pixiv.net
>>> site = Pixiv()
>>> tags = site.get_tags()
>>> len(tags.data.tags) > 10
True
"""
from smarthttp.sites.galleries import *

class Pixiv(SpecificSite):
    domain = 'www.pixiv.net'
    proto  = 'http'

    def login(self, username, password):
        data = {'mode':'login', 'pass':password, 'pixiv_id':username}
        req = self.request('index.php', data=data)
        if 'location' in req.headers and 'mypage' in req.headers['location']:
            mp = self.request('mypage.php')
            return self.ok(True)
        else:
            return self.error("Could not login")
            
    def view_tag_url(self, tag):
        url = u"/tags.php"
        return self.compile_url(url, {'tag':tag})

    def get_tags(self, page=0, r18=False):
        if r18:
            url = u"tags_r18.php"
        else:
            url = u"tags.php"
        req = self.request(self.compile_url(url, {'p':page+1}))
        res = SmartDict({'tags':set(), 'pages':0})
        page_res = self.parse_tags(req)
        return self.ok(page_res.data)
        
    @parser
    def parse_tags(self, req):
        doc = self.assertHTML(req)
        res = SmartDict({'tags':set(), 'pages':0, 'page':0})
        tags_el = self.assertXPath(doc, "/html/body//div[@id='popular_tag']/span")
        for tag_el in tags_el:
            tag = unicode(tag_el[0].text).strip()
            count = int(tag_el[0][0].text)
            res.tags.add(Tag(tag, count, []))
        return self.ok(res)
        
        
