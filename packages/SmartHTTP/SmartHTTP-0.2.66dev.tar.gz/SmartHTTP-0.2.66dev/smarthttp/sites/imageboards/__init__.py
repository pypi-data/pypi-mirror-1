# -*- coding: utf-8 -*-
"""
Module for imageboard engines
"""
from smarthttp.lib.containers import SmartDict, strdict
from smarthttp.sites import SpecificSite, SiteEngine, parser
from datetime import datetime

class Imageboard(SiteEngine):
    pass


class Board(object):
    name = None
    site = None
    threads = None
    def __init__(self, name=None, site=None, threads=None, **kw):
        self.name = name
        self.site = site
        self.threads = set()
        if threads:
            for tdict in threads:
                thread = Thread(board=self, **strdict(tdict))
                self.threads.add(thread)

class Thread(object):
    board = None
    display_id = 0
    posts = None
    title = u''
    archived = False
    invisible = False

    def __init__(self, board, display_id=0, posts=None, title=u'', archived=False, invisible=False, **kw):
        self.board = board
        self.display_id = int(display_id)
        self.title = title
        self.archived = archived
        self.invisible = invisible
        self.posts = set()
        if posts:
            for pdict in posts:
                post = Post(thread=self, **strdict(pdict))
                self.posts.add(post)
                

class Post(object):
    thread = None
    display_id = 0
    post_id    = 0
    date  = None
    message = u""
    subject = u""
    files = None
    name  = u""
    sage  = False
    invisible = False
    inv_reason = u""
    op    = False
    def __init__(self, thread, display_id, post_id, date, message, subject, files, name, sage, op, invisible=False, inv_reason=u"", **kw):
        self.thread = thread
        self.display_id = int(display_id)
        self.post_id = int(post_id)
        self.date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        self.message = message
        self.subject = subject
        self.name = name
        self.sage = sage
        self.invisible = invisible or (self.op and thread.invisible)
        self.inv_reason = inv_reason
        self.op = op
        self.files = set()
        for fdict in files:
            f = File(post=self, **strdict(fdict))
            self.files.add(f)

    @property
    def get_admin_url(self):
        return self.thread.board.site.compile_url("/admin/get_post/{0.post_id}".format(self))

    @property
    def get_url(self):
        return self.thread.board.site.get_post_url(self.display_id, self.thread.display_id, self.thread.board.name)

    @property
    def get_text_files(self):
        return u"".join(map(lambda x:u"{0.ftype}: {0.get_url()} {0.rating}, {0.size} bytes\n".format(x), self.files))

    @property
    def get_invisible(self):
        if self.invisible:
            return u"*INV - {0}* ".format(u', '.join(self.inv_reason))
        else:
            return u""

    @property
    def get_sage(self):
        if self.sage:
            return u"[SAGE] "
        else:
            return u""
    
    def text(self, admin=False):
        sd = SmartDict({}, '')
        if admin:
            if self.op:
                sd.act = u"Новый тред"
            else:
                sd.act = u"Новый пост"
                sd.title = u" в треде '{0.title}'".format(self.thread)
        text = u"{0.get_admin_url} | {0.get_url}, {1.act} {0.post_id}\n"\
               u"{0.get_invisible}{0.get_sage}{0.subject} {0.name} {0.date}{1.title}\n"\
               u"{0.get_text_files}"\
               u"{0.message}".format(self, sd)
        return text

class File(object):
    {"rating": "sfw", "thumb": "thumb/jpg/1002/126696112505642s.jpg", "src": "src/jpg/1002/guts-93324.jpg", "file_id": 165230, "type": "image", "size": 93324}
    post = None
    rating = u"unrated"
    filename = u""
    src = u""
    thumb = u""
    file_id = 0
    ftype = u"image"
    size = 0
    def __init__(self, post, rating, src, thumb, file_id, type, size, filename=u"", **kw):
        self.post = post
        self.rating = rating
        self.filename = filename
        self.size = size
        self.file_id = int(file_id)
        self.thumb = thumb
        self.src = src
        self.ftype = type

    def get_url(self):
        return self.post.thread.board.site.compile_url(self.src)

class Event(object):
    date = None
    event = None
    def __init__(self, date=None, event=None, **kw):
        self.date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        self.event = event

    def text(self, admin=False):
        return u"{0.date} − {0.event}".format(self)
