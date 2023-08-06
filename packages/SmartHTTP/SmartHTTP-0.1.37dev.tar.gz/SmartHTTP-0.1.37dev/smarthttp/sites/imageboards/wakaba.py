# -*- coding: utf-8 -*-
"""
"""
from smarthttp.sites import SiteEngine
from smarthttp.dom import GetPlainText, GetDOM, ForcedEncoding
import re, datetime

class Wakaba(SiteEngine):
    """
    Scraper for wakaba imageboards
    """
    
    def parse_local_file(self, fp):
        data = open(fp, 'r').read().decode('utf-8')
        res = []
        document = GetDOM(data)
        op = document.xpath('//div/blockquote')
        if not op:
            op = document.xpath('//form/blockquote')
        posts = document.xpath('//td/blockquote')
        for post in op + posts:
            text = GetPlainText(post)
            res.append(text)
        return self.result(res)
