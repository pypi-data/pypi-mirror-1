# -*- coding: utf-8 -*-
"""
Client for Google applications
"""
from smarthttp.sites import SpecificSite
from urllib import quote

class Google(SpecificSite):
    domain = u'google.com'
    google_langs =\
  		{ 'af':'Afrikaans','sq':'Albanian','am':'Amharic','ar':'Arabic','hy':'Armenian','az':'Azerbaijani','eu':'Basque'
  		, 'be':'Belarusian','bn':'Bengali','bh':'Bihari','bg':'Bulgarian','my':'Burmese','ca':'Catalan','chr':'Cherokee'
  		, 'zh':'Chinese','zh-CN':'Chinese_simplified','zh-TW':'Chinese_traditional','hr':'Croatian','cs':'Czech','da':'Danish'
  		, 'dv':'Dhivehi','nl':'Dutch','en':'English','eo':'Esperanto','et':'Estonian','tl':'Filipino','fi':'Finnish'
  		, 'fr':'French','gl':'Galician','ka':'Georgian','de':'German','el':'Greek','gn':'Guarani','gu':'Gujarati','iw':'Hebrew'
  		, 'hi':'Hindi','hu':'Hungarian','is':'Icelandic','id':'Indonesian','iu':'Inuktitut','it':'Italian','ja':'Japanese'
  		, 'kn':'Kannada','kk':'Kazakh','km':'Khmer','ko':'Korean','ku':'Kurdish','ky':'Kyrgyz','lo':'Laothian','lv':'Latvian'
  		, 'lt':'Lithuanian','mk':'Macedonian','ms':'Malay','ml':'Malayalam','mt':'Maltese','mr':'Marathi','mn':'Mongolian'
  		, 'ne':'Nepali','no':'Norwegian','or':'Oriya','ps':'Pashto','fa':'Persian','pl':'Polish','pt-PT':'Portuguese'
  		, 'pa':'Punjabi','ro':'Romanian','ru':'Russian','sa':'Sanskrit','sr':'Serbian','sd':'Sindhi','si':'Sinhalese'
  		, 'sk':'Slovak','sl':'Slovenian','es':'Spanish','sw':'Swahili','sv':'Swedish','tg':'Tajik','ta':'Tamil','tl':'Tagalog'
  		, 'te':'Telugu','th':'Thai','bo':'Tibetan','tr':'Turkish','uk':'Ukrainian','ur':'Urdu','uz':'Uzbek','ug':'Uighur','vi':'Vietnamese'
  		}

    def detect_lang(self, text):
        if type(text) == unicode:
            text = text.encode('utf-8')
        text = quote(text)
        data = self.request('http://ajax.googleapis.com/ajax/services/language/detect?v=1.0&q=%s' % (text))
        if data.error:
            return self.error(data.error_text)
        try:
            convert = data.json
            results = convert['responseData']['language']
            return self.ok(results)
        except Exception, e:
            return self.error(e)

    def translate(self, text, from_l='ru', to_l='en'):
        if type(text) == unicode:
            text = text.encode('utf-8')        
        text = quote(text)
        data = self.request('http://ajax.googleapis.com/ajax/services/language/translate?v=1.0&q=%s&langpair=%s%%7C%s' % (text, from_l, to_l))
        if data.error:
            return self.error(data.error_text)
        try:
            convert = data.json
            status = convert['responseStatus']
            results = convert['responseData']['translatedText']
            return self.ok(results)
        except Exception, e:
            return self.error(e)

    def search(self, text):
        if type(text) == unicode:
            text = text.encode('utf-8')        
        text = quote(text)
        data = self.request('http://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=%s&hl=ru' % text)
        if data.error:
            return self.error(data.error_text)
        try:
            convert = data.json
            status = convert['responseStatus']
            results = convert['responseData']['results']
            return self.ok(results)
        except Exception, e:
            return self.error(e)

