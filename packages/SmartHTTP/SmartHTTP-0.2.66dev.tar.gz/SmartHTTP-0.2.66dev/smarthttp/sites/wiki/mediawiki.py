# -*- coding: utf-8 -*-
"""
Client for MediaWiki applications
"""
from BeautifulSoup import BeautifulStoneSoup
from smarthttp.sites import SiteEngine
import re, datetime, urllib
import simplejson

class MediaWikiTemplate(object):
    parent = None
    name   = None
    content = None
    lines  = None
    count_open = 1
    def __init__(self, parent=None, name=None, content=None, lines=None, line=None):
        self.parent = parent
        if name:
            self.name = name.split('|', 1)[0].split('}}', 1)[0].lower()
        self.content = content
        if not lines:
            lines = []
        self.lines = lines
        if line:
            self.lines.append(line)
            self.name = line.split('|', 1)[0].split('}}', 1)[0].lower()

    def add_line(self, line):
        self.count_open += line.count('{{') - line.count('}}')
        if self.count_open == 0:
            line = line.rsplit('}}', 1)[0]
        self.lines.append(line.strip())

    def walk_line(self, line):
        cl = []
        rest = []
        # find where current template ends, and return rest of list
        for i in range(len(line)):
            if i:
                self.count_open += 1
            self.count_open -= line[i].count('}}')
            if self.count_open <= 0:
                cl.append(line[i].rsplit('}}', self.count_open*-1 + 1)[0])
                self.count_open = 0
                rest = line[i+1:]
                break
            cl.append(line[i])            
        self.lines.append(u'{{'.join(cl).strip())
        return rest
    def get_param(self, idx):
        if self.content:
            params = self.content.split('|')
            if len(params) > idx:
                param = params[idx].strip()
                return param
        return None

    def get_wikilinks(self):
        return self.parent.get_wikilinks(content=self.content)

    def __repr__(self):
        return "<Template {{%s}} at %s>" % (self.name, self.parent)

class MediaWikiPageSection(object):
    page = None
    section = None
    level   = None
    content = None
    header  = None
    sections= None
    def __init__(self, page, section, level, content):
        self.page = page
        self.level = level
        self.section = section
        self.content = content

    def get_sections(self):
        if not self.sections:
            self.header, self.sections = self.page.parse_sections(self.content, level+1)
        return self.sections

    def get_templates(self, content=None):
        return self.page.get_templates(content=self.content, parent=self)

    def get_wikilinks(self, content=None):
        if content is None:
            content = self.content
        return self.page.get_wikilinks(content=content)

    def __repr__(self):
        return "<MediaWikiPageSection(%s, %s)>" % (self.section.encode('utf-8'), self.page.title.encode('utf-8'))
        
class MediaWikiPage(object):
    mediawiki = None
    title = None
    page_id = None
    revision_id = None
    ns       = None
    content  = None
    sections = None
    header   = None
    aliases  = None
    re_header = re.compile("""^=(=+)([^=]+)=(=+)$""")
    def __init__(self, mw=None, page_id=None, ns=None, title=None, content=None, aliases=None):
        self.mediawiki = mw
        self.page_id = page_id
        self.ns      = ns
        self.title   = title
        self.content = content
        if aliases is None:
            self.aliases = set()
        else:
            self.aliases = aliases

    @property
    def escaped_title(self):
        return MediaWiki.escaped_title(self.title)

    @property
    def safe_title(self):
        return MediaWiki.safe_title(self.title)

    def load(self):
        data = self.mediawiki.get_page(pages=self)
        if str(self.page_id) in data.data:
            pd = data.data[str(self.page_id)]
            self.content = pd['content']

    def save_to_file(self, path=None, basepath=None):
        if not path and basepath:
            path = u"%s/%s" % (basepath, self.safe_title)
        out = open(path, 'w')
        out.write((u"%s|%s|%s\n%s" % (self.page_id, self.ns, self.title, self.content)).encode('utf-8'))
        out.close()

    @classmethod
    def load_from_file(cls, path):
        data = open(path, 'r').read().decode('utf-8').split('\n', 1)
        params = data[0].split('|', 3)
        return cls(page_id=int(params[0]), ns=params[1], title=params[2], content=data[1])

    def get_sections(self):
        if not self.sections:
            self.header, self.sections = self.parse_sections(self.content, 1)
        return self.sections

    def parse_sections(self, content, level):
        header = []
        current_section = ""
        csl = header
        sections = {}
        lines = map(lambda x:x.strip(), content.split('\n'))
        for l in lines:
            matched = False
            if l:
                m = self.re_header.match(l)
                if m:
                    g = m.groups()
                    if len(g[0]) == len(g[2]) and len(g[0]) == level:
                        current_section = g[1].strip()
                        if not current_section in sections:
                            sections[current_section] = []
                        csl = sections[current_section]
                        matched = True
            if not matched:
                csl.append(l)
        header = u"\n".join(header)
        result = {}
        for section in sections:
            result[section] = MediaWikiPageSection(page=self, section=section, level=level, content=u"\n".join(sections[section]))
        return header, result

    def get_templates(self, content=None, parent=None):
        """
        {{a}}
        {{b|}}
        {{c|d}}
        {{e}}{{f}}
        {{g|h={{j}}}}
        {{k|l={{n}}}}{{m}}
        """
        if content is None:
            content = self.content
        if not parent:
            parent = self
        lines = map(lambda x:x.strip(), content.split('\n'))
        templates = {}
        current = None
        for l in lines:
            if not '<!--' in l:
                if '{{' in l:
                    ls = l.split('{{')
                    if '}}' in l:
                        if current:
                            rest = current.walk_line(ls)
                            if current.count_open == 0:
                                current.content = u'\n'.join(current.lines)
                                current = None
                        else:
                            rest = ls[1:]
                        if rest:
                            while rest:
                                lp = rest[0]
                                current = MediaWikiTemplate(parent=parent, name=lp)
                                templates.setdefault(current.name, [])
                                templates[current.name].append(current)
                                rest = current.walk_line(rest)
                                if current.count_open == 0:
                                    current.content = u'\n'.join(current.lines)
                                    current = None                                
                    elif current:
                        current.add_line(l)
                    else:
                        current = MediaWikiTemplate(parent=parent, line=ls[1])
                        templates.setdefault(current.name, [])
                        templates[current.name].append(current)
                elif current:
                    current.add_line(l)
            elif current:
                current.add_line(l)
            if current and current.count_open == 0:
                current.content = u'\n'.join(current.lines)
                current = None
        return templates
                
    # [[Link|Repr]] -> (Link, "|Repr", Repr)
    re_wikilinks = re.compile(r"""\[\[([^\]\|]+)(\|([^\]]*))?\]\]""")
    def get_wikilinks(self, content=None):
        """
        Notice: links may contain : and #!, ex. [[Image:Something]], [[WikiPedia:Something]] [[Article#Section]]
        """
        links = {}
        if content is None:
            content = self.content
        lines = map(lambda x:x.strip(), content.split('\n'))
        for l in lines:
            if l and not '<!--' in l:
                m = self.re_wikilinks.findall(l)
                if m:
                    for match in m:
                        link = match[0]
                        name = match[2]
                        if not name:
                            name = link
                        if '#' in link:
                            link = link.split('#', 1)[0].strip()
                        if link:
                            link = MediaWiki.escaped_title(link)
                            if not link in links:
                                links[link] = []
                            links[link].append((link, name))
        return links

    def __repr__(self):
        return "<MediaWikiPage(%s)>" % (self.title.encode('utf-8'))

class MediaWiki(SiteEngine):
    pages_list_limit = 500
    pages_content_limit = 50
    def __init__(self, pages_list_limit=500, pages_content_limit=50, *args, **kw):
        SiteEngine.__init__(self, *args, **kw)
        self.pages_content_limit = 50
        self.pages_list_limit = 500
    def get_list(self, ns='', from_='', limit=500):
        if from_:
            if type(from_) == unicode:
                from_ = from_.encode('utf-8')
            from_ = urllib.quote(from_)
        
        url = '/api.php?action=query&list=allpages&format=json&apfilterredir=nonredirects&aplimit=%s%s%s' % (limit,
                                                                                                             from_ and '&apfrom=%s' % from_ or '',
                                                                                                             ns and '&apnamespace=%s' % ns or '')
        req = self.request(url)
        if req.error or req.code != 200:
            return self.error_http(req)
        data = simplejson.loads(req.data)
        res = {}
        if 'query-continue' in data:
            res['next'] = data['query-continue']['allpages']['apfrom']
        else:
            res['next'] = None
        res['pages'] = []
        for pd in data['query']['allpages']:
            page = MediaWikiPage(self, pd['pageid'], pd['ns'], pd['title'])
            res['pages'].append(page)
        return self.result(res)

    def get_page(self, title=None, page_id=None, revision=None, pages=None):
        if title and type(title) != list and type(title) != set:
            title = [title]
        if page_id and type(page_id) != list and type(page_id) != set:
            page_id = [page_id]
        if pages and type(pages) != list:
            pages = [pages]

	instanced = {}
	if pages:
	    if not page_id:
	        page_id = []
	    for page in pages:
	        page_id.append(str(page.page_id))
	        instanced[page.title] = page
	        
        base_url = '/api.php?action=query&prop=revisions&rvprop=content&format=json&redirects'

        results = []
        redirects = {}
        aliases   = {}
        missing   = set()
        while title or page_id:
            if title:
                req = title[:self.pages_content_limit]
                title = title[self.pages_content_limit:]
                url = self.compile_url(base_url,
                                       {'titles':u'|'.join(req)})
            elif page_id:
                req = page_id[:self.pages_content_limit]
                page_id = page_id[self.pages_content_limit:]
                url = self.compile_url(base_url,
                                       {'pageids':u'|'.join(req)})
            req = self.request(url)
            if req.error or req.code != 200:
                return self.error_http(req)
            data = simplejson.loads(req.data)
            if 'query' in data:
                self.log.info(data['query'].keys())
                if 'normalized' in data['query']:
                    for redir in data['query']['normalized']:
                        redirects[redir['from']] = redir['to']
                        aliases.setdefault(redir['to'], set())
                        aliases[redir['to']].add(redir['from'])
                if 'redirects' in data['query']:
                    for redir in data['query']['redirects']:
                        redirects[redir['from']] = redir['to']
                        aliases.setdefault(redir['to'], set())
                        aliases[redir['to']].add(redir['from'])                        
                if 'pages' in data['query']:
                    for pid in data['query']['pages']:
                        if int(pid) > -1:
                            pd = data['query']['pages'][pid]
                            pageid = 'pageid' in pd and pd['pageid'] or int(pid)
                            content = 'revisions' in pd and unicode(pd['revisions'][0]['*']) or u''
                            page_title   = unicode(pd['title'])
                            page_aliases = aliases.get(page_title, set())
                            if page_title in instanced:
                                page = instanced[page_title]
                                page.content = content
                                page.aliases = page.aliases.union(page_aliases)
                            else:
                                page = MediaWikiPage(self, page_id=pageid, ns=pd['ns'], title=page_title, content=content, aliases=page_aliases)
                            results.append(page)
                        else:
                            missing.add(unicode(data['query']['pages'][pid]['title']))
            elif not results:
                self.log.warn(u"No 'query' in data: %s" % data.keys())
            else:
                self.log.warn(u"No 'query' in data: %s" % data.keys())
        self.log.info(redirects)
        return self.result({'pages':results, 'redirects':redirects, 'missing':missing, 'aliases':aliases})

    @classmethod
    def escaped_title(cls, title):
        # normalize spaces
        title = u' '.join(filter(bool, title.replace('_', ' ').split(' ')))
        # remove weird chars. Basically they should not be there in the first place, but lets be fail-proof
        title = title.replace(u'‎', u'').replace(u'|', u'').replace(u'}', u'').replace(u'{', u'')
        # unquote
        if '%' in title:
            title = urllib.unquote(title.encode('utf-8')).decode('utf-8')
        # unescape html entities
        if '&' in title:
            title = BeautifulStoneSoup(title, convertEntities=BeautifulStoneSoup.HTML_ENTITIES).contents[0]
        # Capitalize first letter
        title = title[0].upper() + title[1:]
        return title

    @classmethod
    def safe_title(cls, title):
        # Let it be normalized title with spaces and slashes to _
        title = cls.escaped_title(title)
        return title.replace(' ', '_').replace('/', '_')
