# -*- coding: utf-8 -*-
"""
"""
from smarthttp.sites import SpecificSite
from smarthttp.dom import GetPlainText, GetDOM, ForcedEncoding
import re, datetime

class NullChan(SpecificSite):
    """
    Scraper for 0chan.ru imageboard
    """
    
    def parse_local_file(self, fp):
        data = open(fp, 'r').read().decode('utf-8')
        res = []
        document = GetDOM(data)
        posts = document.xpath("//div[@class='postmessage']")
        for post in posts:
            text = GetPlainText(post)
            res.append(text)
        return self.result(res)
