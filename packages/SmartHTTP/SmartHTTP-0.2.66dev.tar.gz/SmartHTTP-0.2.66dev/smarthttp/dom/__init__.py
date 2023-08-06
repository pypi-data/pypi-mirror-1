from lxml import etree
import StringIO
import logging
log = logging.getLogger(__name__)
html_parser = etree.HTMLParser()

def GetNextTag(el, tag, skip=0):
    tag = tag.lower()
    if skip:
        r = el.getnext()
    else:
        r = el
    if not r.tag or r.tag.lower() != tag:
        while (r.getnext() != None) and not (r.getnext().tag and r.getnext().tag.lower() == tag):
            r = r.getnext()
        if r.getnext() != None:
            r = r.getnext()
    if r.tag and r.tag.lower() == tag:
        return r
    else:
        return None
    
def GetPreviousTag(el, tag, skip=0):
    tag = tag.lower()
    if skip:
        r = el.getprevious()
    else:
        r = el
    if not r.tag or r.tag.lower() != tag:
        while (r.getprevious() != None) and not (r.getprevious().tag and r.getprevious().tag.lower() == tag):
            r = r.getprevious()
        if r.getprevious() != None:
            r = r.getprevious()
    if r.tag and r.tag.lower() == tag:
        return r
    else:
        return None

def GetTextBetween(text, start, end):
    start_pos = text.find(start)
    end_pos = text.find(end)
    if start_pos >= 0 and end_pos >= 0:
        start_pos += len(start)
        return text[start_pos:end_pos]
    else:
        return None

def GetDOM(rawhtml):
    document = etree.parse(StringIO.StringIO(rawhtml), html_parser)
    return document

def GetPlainText(node=None, text=u'', rawhtml=u''):
    if rawhtml and node is None:
        node = GetDOM(rawhtml).getroot()
    if node.tag != etree.Comment and node.text:
        if text and text[-1] != ' ':
            text += ' '
        text += node.text
    if node.tag != etree.Comment and len(node)>0:
        for n in node:
            text = GetPlainText(n, text)
    if node.tail:
        if text and text[-1] != ' ':
            text += ' '        
        text += node.tail
    return text


def ForcedEncoding(text, enc):
    return u''.join(map(lambda x:x.decode(enc), map(chr, filter(lambda x:x < 256, map(ord, text)))))
