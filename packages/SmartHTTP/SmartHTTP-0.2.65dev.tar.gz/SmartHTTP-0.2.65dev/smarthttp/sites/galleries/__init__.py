# -*- coding: utf-8 -*-
"""
Image gallery sites
"""
from smarthttp.lib.containers import SmartDict
from smarthttp.sites import SpecificSite, SiteEngine, parser

class Tag(object):
    tag = None
    count = 0
    types = None
    def __init__(self, tag=None, count=0, types=None):
        if type(tag) == str:
            tag = unicode(tag)
        elif type(tag) != unicode:
            raise ValueError(u"Tag should be string")
        self.tag = tag
        if type(count) != int:
            count = int(count)
        self.count = count
        if type(types) != list and type(types) != set:
            types = []
        self.types = types
