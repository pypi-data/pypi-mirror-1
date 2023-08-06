# -*- coding: utf-8 -*-
"""
Client for Shimmie and Shimmie 2 applications
http://12ch.ru/macro/index.php
http://www.animemahou.com/tags/list
http://yaranaiko.net/
http://thedoi.net/post/list
http://booru.nanochan.org/tags/popularity
http://angelhq.net/
http://rule34.paheal.net/post/list
http://www.tentaclerape.net/imageboard/index.php
http://dontstickthatthere.com/shimmie/post/list
http://munemune.net/index.php?q=/post/list
http://vgb-portal.com/chan/post/list
http://chan.aniview.eu/post/list
http://gallery.burrowowl.net/
http://www.clubetchi.com/gpx/post/list
>>> site = Shimmie2(url='http://angelhq.net/')
>>> tags = site.get_tags(order='count')
>>> len(tags.data.tags) > 10
True
"""
from smarthttp.lib.containers import SmartDict
from smarthttp.sites.galleries import Tag
from smarthttp.sites import SiteEngine, parser

class Shimmie2(SiteEngine):
    proto = 'http'

    def view_tag_url(self, tag, page=1, **kw):
        kw = SmartDict(kw, "")._join({'tag':tag, 'page':page})
        url = u"/post/list/{0.tag}/{0.page}".format(kw)
        return self.compile_url(url)

    def get_tags(self, **kw):
        kw = SmartDict(kw, "")
        url = u'/tags/popularity'
        req = self.request(self.compile_url(url))
        page_res = self.parse_tags(req)
        return self.ok(page_res.data)

    @parser
    def parse_tags(self, req):
        doc = self.assertHTML(req)
        res = SmartDict({'tags':set(), 'pages':0})
        tags = self.assertXPath(doc, '/html/body/div/div/p/a')
        for tag_a in tags:
            tag_s = tag_a.text.rsplit(u'\xa0', 1)
            count = int(tag_s[1].split('(', 1)[1].split(')', 1)[0])
            res.tags.add(Tag(tag=tag_s[0], count=count))
        return self.ok(res)        
