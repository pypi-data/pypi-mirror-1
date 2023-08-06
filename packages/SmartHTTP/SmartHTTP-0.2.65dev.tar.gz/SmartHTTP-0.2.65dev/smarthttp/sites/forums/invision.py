# -*- coding: utf-8 -*-
"""
"""
from smarthttp.sites import SiteEngine
from smarthttp.dom import GetPlainText, GetDOM, ForcedEncoding
import re, datetime

class InvisionPowerBoard(SiteEngine):
    """
    Scraper for IPB forum
    """
    
    def parse_local_file(self, fp):
        data = open(fp, 'r').read().decode('cp1251')
        res = []
        document = GetDOM(data)
        posts = document.xpath("//div[@class='postcolor']")
        for post in posts:
            exc = post.xpath("./div") + post.xpath("./span[@class='edit']") + post.xpath("./noindex")
            for el in exc:
                post.remove(el)
            text = GetPlainText(post)
            res.append(text)
        return self.result(res)
