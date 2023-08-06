# -*- coding: utf-8 -*-
u"""
==Regions==

The United States is composed of 50 '''states''', as well as the city of [[Washington D.C.]], a federal district and the nation's capital. 
* Some hotels have "business centers" where you can use a computer connected to the internet, fax a message, use a printer and make copies.
[[WikiPedia:United States]]
[[Dmoz:North America/United States/]]
[[World66:northamerica/unitedstates]]
{{IsPartOf|Kunashir‎}}
{{IsPartOf|Khorezm|}}
{{isPartOf|Friesland}}}
{{ml
}}
{{a}}
{{b|}}
{{c|d}}
{{e}}{{f}}
{{g|h={{j}}}}
{{k|l={{n}}}}fdsfsdf}} {{m}}
"""
from smarthttp.sites.wiki.mediawiki import MediaWiki, MediaWikiPage
mw = MediaWiki()
page = MediaWikiPage(mw, title='test', content=__doc__)
sections = page.get_sections()
regions = sections['Regions']
templates = regions.get_templates()
print templates.keys()
print templates['k'][0].content
print templates['k'][0].get_param(1)
