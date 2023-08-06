# -*- coding: utf-8 -*-
"""
"""
from smarthttp.sites import SpecificSite
from smarthttp.dom import GetPlainText, GetDOM, ForcedEncoding
import re, datetime

class BashOrgRu(SpecificSite):
    """
    Scraper for bash.org.ru
    """
    domain = 'bash.org.ru'
    
    def parse_local_file(self, fp):
        data = open(fp, 'r').read()
        res = []
        document = GetDOM(data)
        cites = document.xpath("//div[@class='q']/div[2]")
        for cite in cites:
            text = ForcedEncoding(GetPlainText(cite), 'cp1251')
            res.append(text)
        return self.result(res)
