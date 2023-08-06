# -*- coding: utf-8 -*-
"""
Client for nomina.ru
>>> nomina = Nomina()
>>> res = nomina.search(domain='nomina.ru')
>>> len(res.data) == 1
True
"""
from smarthttp.lib.containers import SmartDict
from smarthttp.sites import SpecificSite, parser

class Nomina(SpecificSite):
    domain = 'www.nomina.ru'
    proto = 'http'
    def search(self, **kw):
        kw = SmartDict(kw, "")
        url = u"/search/search_by_value.php?domain={0.domain}&owner={0.owner}&nserver={0.nserver}&email={0.email}&phone={0.phone}&fax_no={0.fax}&created={0.created}&paid_till=&free_date=&humip={0.ip}&registrar={0.registrar}".format(kw)
        page = 0
        pages = 1
        domains = set()
        while page < pages:
            req = self.request(self.compile_url(url, {'page':page}))
            page_res = self.parse_search(req)
            if page_res:
                pages = page_res.data.pages
                for domain in page_res.data.domains:
                    domains.add(domain)
            else:
                self.log.warn(page_res.error_text)
            page += 1
        return self.ok(domains)
        
    @parser
    def parse_search(self, req):
        self.assertHTML(req)
        td = self.assertXPathOne(req.document, '/html/body/table/tr[4]/td[2]')
        res = SmartDict({'pages':0}, set)
        domains = td.xpath('./table//a')
        pages_p = self.assertXPathOne(td, './/p[4]')
        pages_a = pages_p.xpath('.//a')
        res.pages = len(pages_a) + 1
        for dom in domains:
            res.domains.add(unicode(dom.text).strip())
        return self.ok(res)
        
