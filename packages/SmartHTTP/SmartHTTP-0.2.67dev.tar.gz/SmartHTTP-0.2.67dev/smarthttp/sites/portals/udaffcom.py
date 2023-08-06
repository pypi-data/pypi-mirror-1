# -*- coding: utf-8 -*-
"""
"""
from smarthttp.sites import SpecificSite
from smarthttp.dom import GetPlainText, GetDOM, ForcedEncoding
import re, datetime

class UdaffCom(SpecificSite):
    """
    Scraper for udaff.com
    """
    domain = 'udaff.com'
    
    def parse_local_file(self, fp):
        data = open(fp, 'r').read()
        res = []
        document = GetDOM(data)
        res.append(GetPlainText(document.xpath("//div/div[@class='text']")[0]))
        comments = document.xpath("//td[@class='main_center']//td/div[@class='text']")
        for post in comments:
            text = GetPlainText(post)
            res.append(text)
        return self.result(res)
