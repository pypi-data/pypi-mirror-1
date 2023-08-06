# -*- coding: utf-8 -*-
"""
Client for infoseek.co.jp
"""
from smarthttp.sites import SpecificSite

class Infoseek(SpecificSite):
    def __init__(self, *t, **d):
        SpecificSite.__init__(self, *t, **d)
        self.token = None

    def prepare(self):
        req = self.request('http://translation.infoseek.co.jp/')
        self.get_token(req)

    def get_token(self, req):
        token_input = req.dom.xpath("/html/body/div//input[@name='token']")[0] 
        self.token = token_input.get("value")
        
    def translate(self, word=None, from_l='ja', to_l='en'):
        if not self.token:
            self.prepare()
        if type(word) == unicode:
            word_enc = word.encode('utf-8')
        else:
            word_enc = word
        if to_l == 'en' and from_l == 'ja':
            selector = '1'
        else:
            selector = '0'
        data = {'ac':'Text', 'lng':'en', 'original':word_enc, 'selector':selector, 'token':self.token, 'submit':'　翻訳'}
        req = self.request('http://translation.infoseek.co.jp/', request="POST", data=data)
        self.get_token(req)
        document = req.dom
        converted = document.xpath("/html/body/div//textarea[@name='converted']")[0]
        word = converted.text
        if type(word) == str:
            word = unicode(word, 'utf-8')
        self.log.info("Word: %s, token: %s" % (word, self.token))
        return self.ok(word)
