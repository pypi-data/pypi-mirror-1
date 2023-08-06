# -*- coding: utf-8 -*-
"""
Client for gelbooru.com
>>> site = Gelbooru()
>>> tags = site.get_tags(order='index_count')
>>> len(tags.data.tags) > 10
True
"""
from smarthttp.lib.containers import SmartDict
from smarthttp.sites.galleries import Tag
from smarthttp.sites import SpecificSite, parser

class Gelbooru(SpecificSite):
    domain = 'gelbooru.com'
    proto = 'http'

    def view_tag_url(self, tag):
        url = u"/index.php"
        return self.compile_url(url, {'page':'post', 's':'list', 'tags':tag})

    def get_tags(self, page=0, name='all', sort='desc', order='index_count', **kw):
        """
        http://gelbooru.com/index.php?page=tags&s=list&tags=all&sort=desc&order_by=index_count
        """
        kw = SmartDict(kw, "")._join({'name':name, 'sort':sort, 'order':order})
        kw.pid = page * 50
        url=u"index.php?page=tags&s=list&tags={0.name}&sort={0.sort}&order_by={0.order}&pid={0.pid}".format(kw)
        req = self.request(self.compile_url(url))
        res = SmartDict({'tags':set(), 'pages':0})
        page_res = self.parse_tags(req)
        
        res.tags = page_res.data
        
        return self.ok(res)

    @parser
    def parse_tags(self, req):
        doc = self.assertHTML(req)
        rows = doc.xpath("/html/body/div[@id='content']/table/tr")
        if len(rows) > 1:
            rows.pop(0)
            tags = []
            for row in rows:
                count = int(row[0].text)
                tag   = row[1][0][0].text
                types = map(lambda x:x.strip(), row[2].text.split('(')[0].split(','))
                tags.append(Tag(tag, count, types))
            return self.ok(tags)
        else:
            return self.error('Nothing found')

