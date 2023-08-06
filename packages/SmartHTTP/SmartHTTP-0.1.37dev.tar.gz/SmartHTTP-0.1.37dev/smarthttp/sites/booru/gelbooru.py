# -*- coding: utf-8 -*-
"""
Client for gelbooru.com
"""
from smarthttp.sites import SpecificSite

class Gelbooru(SpecificSite):
    domain = 'gelbooru.com'
    proto = 'http'
    def get_tags(self, search=None, page=0, order='index_count', sort='desc'):
        """
        http://gelbooru.com/index.php?page=tags&s=list&tags=all&sort=desc&order_by=index_count
        """
        if not search:
            search = 'all'
        pid = page*50
        req = self.request('index.php?page=tags&s=list&tags=%s&sort=%s&order_by=%s&pid=%s' % (search, sort, order, pid))
        doc = req.dom
        rows = doc.xpath("/html/body/div[@id='content']/table/tr")
        if len(rows) > 1:
            rows.pop(0)
            tags = []
            for row in rows:
                count = int(row[0].text)
                tag   = row[1][0][0].text
                types = map(lambda x:x.strip(), row[2].text.split('(')[0].split(','))
                tags.append({'tag':tag, 'count':count, 'types':types})
            return self.ok(tags)
        else:
            return self.error('Nothing found')

