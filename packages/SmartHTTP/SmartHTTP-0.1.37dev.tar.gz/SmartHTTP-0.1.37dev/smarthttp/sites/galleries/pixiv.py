# -*- coding: utf-8 -*-
"""
Client for www.pixiv.net
"""
from smarthttp.sites import SpecificSite

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

    def get_tags(self, page=0, r18=False):
        if r18:
            url = "tags_r18.php"
        else:
            url = "tags.php"
        url = "%s?p=%s" % (url, page+1)
        req = self.request(url)
        doc = req.dom
        tags = []
        tags_el = doc.xpath("/html/body//div[@id='popular_tag']/span")
        for tag_el in tags_el:
            tag = unicode(tag_el[0].text).strip()
            count = int(tag_el[0][0].text)
            # 'types':(r18 and ['R-18'] or [])
            tags.append({'tag':tag, 'count':count, 'types':[]})
        return self.ok(tags)
        
        
