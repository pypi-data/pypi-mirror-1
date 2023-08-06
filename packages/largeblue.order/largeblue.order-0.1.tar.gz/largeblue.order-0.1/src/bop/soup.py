#!/usr/local/env/python
#############################################################################
# Name:         soup.py
# Purpose:      Support for tag extraction and modification
# Maintainer:
# Copyright:    (c) 2004 iwm-kmrc.de KMRC - Knowledge Media Research Center
# Licence:      GPL
#############################################################################
__docformat__ = 'restructuredtext'

import cache
import helper

try:
    from chardet import detect
except ImportError:
    
    def detect(source):
        for enc in 'ascii', 'iso-8859-1', 'utf-8':
            try:
                unicode(source, encoding=enc)
                return dict(encoding=enc, confidence=0.5)
            except UnicodeDecodeError:
                pass
        return dict(encoding='ascii', confidence=0.0)             


class Tag(object):
    """Represents a HTML tag that can be searched and extracted in the soup."""
    
    self_closing = set(['br', 'hr', 'input', 'img', 'meta', 'embed',
                                    'spacer', 'link', 'frame', 'base'])
    
    def __init__(self, soup, name):
        name = name.lower()
        self.soup = soup
        self.name = name
        self.open = '<%s' % name
        self.close = '</%s>' % name
        self.tag_length = len(self.open)
        self.start = 0
        self.end = 0
        
    def findAttr(self, key):
        s = self.soup.source[self.start:self.closed]
        found = s.find(key + '=')
        if found > -1:
            start = found + len(key) + 1
            value = s[start:]
            first = 1
            if value[0] == '"':
                end = value.find('"', 1)
            elif value[0] == "'":
                end = value.find("'", 1)
            else:
                first = value.find('"', 0) + 1
                end = value.find('"', first)
            value = value[first:end]
            return value, start, end
        return None

    def get(self, key, default=None):
        found = self.findAttr(key)
        if found is not None:
            return self.unicode(found[0])
        return default
        
    def __setitem__(self, key, value):
        found = self.findAttr(key)
        if found is None:
            s = '%s="%s" ' % (key, value)
            index = self.start + self.tag_length + 1
            self.soup.insert(index, index, s)
        else:
            start = self.start + found[1] + 1
            end = start + len(found[0])
            self.soup.insert(start, end, value)
        
    def __delitem__(self, key):
        found = self.findAttr(key)
        if found is not None:
            size = len(found[0])
            start = self.start + found[1] - (len(key) + 1)
            end = self.start + found[1] + size + 2
            self.soup.insert(start, end, '')
            self.end -= size + len(key) + 1
            self.closed -= size + len(key) + 1
 
    @property
    def contents(self):
        end = self.closed - self.start - len(self.close)
        s = str(self)[self.end - self.start: end]
        return [unicode(s, self.soup.encoding)]
        
    @property
    def string(self):
        return u''.join(self.contents).strip()
        
    def unicode(self, s):
        if isinstance(s, unicode):
            return s
        try:
            return unicode(s, self.soup.encoding)
        except UnicodeDecodeError:
            helper.printTrace('Cannot decode unicode')
            return unicode(s, self.soup.encoding, 'replace')
            
    def __str__(self):
        return self.soup.source[self.start:self.closed]
    
    def __repr__(self):
        return str(self)
        
    def __unicode__(self):
        s = self.soup.source[self.start:self.closed]
        return self.unicode(s)
        
    def matching(self, index):
        """Does the complete tag pattern match?"""
        lower = self.soup.lower
        tag_end = index + self.tag_length
        self.end = lower.find('>', index) + 1
        if self.name in self.self_closing:
            self.closed = self.end   
        elif lower[self.end-2] == '/':
            self.closed = self.end
        else:
            self.closed = lower.find(self.close, index) + len(self.close)
            
        valid = lower[tag_end] == '>' or lower[tag_end].strip() == ''
        return valid and self.end > index
        
    def find(self):
        if self.end < 0:
            return False
        if self.start > 0:
            self.start = self.end
        lower = self.soup.lower
        index = lower.find(self.open, self.start)
        while index > -1 and not self.matching(index):
            newindex = lower.find(self.open, index)
            if newindex == index:       # we made no progress
                return False
            index = newindex
        self.start = index
        if index < 0:
            return False
        return True
        
        
class Soup(object):
    """A replacement of the BeautifulSoup parser which is intended to
    work with arbitrary input data, including binary ones which 
    BeautifulSoup isn't able to parse.
    """

    encodings = 'ascii', 'utf-8'
    encoding = 'ascii'
    
    def __init__(self, source, fromEncoding=None):
        self.source = source
        self.lower = source.lower()
        if fromEncoding:
            self.encoding = fromEncoding
        else:
            enc = None
            for meta in self.findAll('meta'):
                ct = meta.get('content')
                if ct:
                    for part in ';'.split(ct):
                        if 'charset=' in part.lower():
                            part = part.replace('charset=')
                            enc = part.strip()
            if not enc:
                enc = detect(source)['encoding']
            self.encoding = enc

    @property
    def originalEncoding(self):
        return self.encoding

    def findAll(self, tag):
        """Iterates over all matching tags in the soup."""
        tag = Tag(self, tag)
        old = -1
        while tag.find():
            new = tag.start
            if old == new:
                return
            yield tag
            old = new

    def first(self, tag):
        """Returns the first matching tag in the soup."""
        tag = Tag(self, tag)
        if tag.find():
            return tag
        return None
        
    def insert(self, start, end, s):
        if isinstance(s, unicode):
            s = s.encode(self.encoding)
        self.source = self.source[:start] + s + self.source[end:]
        self.lower = self.source.lower()
        
    def __unicode__(self):
        if isinstance(self.source, unicode):
            return self.source
        try:
            return unicode(self.source, self.encoding)
        except UnicodeDecodeError:
            helper.printTrace('Cannot decode unicode')
            return unicode(self.source, self.encoding)
            
        

soupCache = cache.Cache()

def cachedSoup(html, fromEncoding=None):
    if html in soupCache:
        return soupCache[html]
    soup = Soup(html, fromEncoding)
    soupCache[html] = soup
    return soup

