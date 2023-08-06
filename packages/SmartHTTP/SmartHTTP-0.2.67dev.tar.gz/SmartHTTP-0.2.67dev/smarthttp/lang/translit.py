# -*- coding: utf-8 -*-
import logging
import sys, os
from smarthttp.lang import split_by_unicode_blocks
log = logging.getLogger(__name__)

translist = open(os.path.join(os.path.dirname(__file__), 'translit.txt')).read().decode('utf-8').split('\n')
transmap = {}
for r in translist:
    if r and r[0] != '#':
        row = r.strip().split()
        if len(row) > 1:
            if len(row) > 2:
                transmap[row[0]] = (row[1], row[2])
            else:
                transmap[row[0]] = (row[1], None)

def transliterate(text):
    trans = []
    parts = split_by_unicode_blocks(text)
    for part in parts:
        i = 0
        while i < len(part[0]):
            c = part[0][i]
            t = None
            if i+1 < len(part[0]):
                p = part[0][i:i+2]
                t = transmap.get(p, None)
                if t:
                    i += 1
            if not t:
                t = transmap.get(c, (c, None))
            if len(part[0]) > 1 and t[1]:
                trans.append(t[1])
            else:
                trans.append(t[0])
            i += 1
    return u''.join(trans)

if __name__ == '__main__':
    print sys.argv[1]
    txt = sys.argv[1]
    if type(txt) == str:
        txt = unicode(txt, 'utf-8')
    print transliterate(txt)
