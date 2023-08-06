# -*- coding: utf-8 -*-
"""
Danbooru gallery engine
>>> site = Danbooru(url='http://danbooru.donmai.us/')
>>> tags = site.get_tags(order='count')
>>> len(tags.data.tags) == 50
True
"""
from smarthttp.lib.containers import SmartDict
from smarthttp.sites.galleries import Tag
from smarthttp.sites import SiteEngine, parser

class Danbooru(SiteEngine):
    proto = 'http'

    def view_tag_url(self, tag):
        url = u"/post/index"
        return self.compile_url(url, {'tags':tag})
    
    def get_tags(self, order='count', **kw):
        kw = SmartDict(kw, "")._join({'order':order})
        url=u"/tag?type={0.type}&commit=Search&name={0.name}&order={0.order}".format(kw)
        req = self.request(self.compile_url(url, {'page':kw.page}))
        res = SmartDict({'tags':set(), 'pages':0})
        page_res = self.parse_tags(req)
        return self.ok(page_res.data)
    
    @parser
    def parse_tags(self, req):
        doc = self.assertHTML(req)
        tbody = self.assertXPathOne(doc, "/html/body/div[@id='content']/table/tbody")
        tags  = tbody.xpath('./tr')
        res = SmartDict({'tags':set(), 'pages':0, 'page':0})
        for tag_tr in tags:
            tds = self.assertXPath(tag_tr, './td', 3)
            count = int(tds[0].text)
            name  = tds[1][-1].text
            types = map(lambda x:x.strip(), tds[2].text.split('(')[0].split(','))
            if name:
                res.tags.add(Tag(name, count, types))
        paginator = self.assertXPathOne(doc, "/html/body/div[@id='content']/div/div[@class='pagination']")
        curr = self.assertXPathOne(paginator, "./span[@class='current']")
        pages = self.assertXPath(paginator, './a')
        res.page = int(curr.text)
        res.pages = int(pages[-2].text)
        return self.ok(res)

