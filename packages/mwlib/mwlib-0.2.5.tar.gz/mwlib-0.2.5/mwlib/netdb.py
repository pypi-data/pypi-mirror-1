#! /usr/bin/env python

# Copyright (c) 2007, PediaPress GmbH
# See README.txt for additional licensing information.

## http://mw/index.php?title=Image:Bla.jpg&action=raw
## http://mw/index.php?title=Template:MYHEADER&action=raw


import os
import shutil
import sys
import urllib
import urllib2
import md5
import time
import tempfile
import re

from mwlib import uparser
from mwlib.log import Log

log = Log("netdb")

sys.getfilesystemencoding = lambda: 'utf-8'

def hashpath(name):
    assert isinstance(name, unicode), "must pass unicode object to hashpath"    
    name = name.replace(" ", "_")
    m=md5.new()
    m.update(name.encode('utf-8'))
    d = m.hexdigest()
    return "/".join([d[0], d[:2], name])

class ImageDB(object):
    def __init__(self, baseurl, localpath=None):
        """
        @param baseurl: base URL or tuple containing several base URLs
        @type localpath: str
        """
        
        if isinstance(baseurl, unicode):
            baseurl = (baseurl.encode('ascii'),)
        elif isinstance(baseurl, tuple):
            baseurl = tuple([bu.encode('ascii') for bu in baseurl if isinstance(bu, unicode)])
        self.baseurl = baseurl
            
        self.localpath = localpath
        self.tmpdir = None
        if not localpath:
            self.tmpdir = unicode(tempfile.mkdtemp())
            self.localpath = self.tmpdir
    
    def _transform_name(self, name):
        """
        @type: unicode
        
        @rtype: unicode
        """
        
        assert isinstance(name, unicode), 'name must be unicode'
        name = name[0].upper() + name[1:]
        return name.replace(' ', '_')
    
    def getDiskPath(self, name, width=None):
        p = self.getPath(name, width=width)
        if p:
            p = os.path.join(self.localpath, p)
        return p

    def getPath(self, name, width=None):
        if not name:
            return None
        name = name[:1].upper()+name[1:]
        
        hp = hashpath(name)

        if width:
            if name.endswith('svg'):
                name = "%s.png" % name
            hpWidth = 'thumb/%s/%dpx-%s' % (hp,width,self._transform_name(name))
        elif name.endswith('svg'):
            return
        
        d = None
        for bu in self.baseurl:
            if width:
                filename = hpWidth
                d = self._fetchURL(bu, hpWidth)
            if d is None:
                filename = hp
                d = self._fetchURL(bu, hp)
            if d is not None:
                break

        if d is None:
            return
        
        dest = os.path.join(self.localpath, filename).encode(sys.getfilesystemencoding() or 'utf-8')
        dn = os.path.dirname(dest)
        if not os.path.exists(dn):
            os.makedirs(dn)
        open(dest, 'wb').write(d)
        return dest

    def _fetchURL(self, baseurl, hp):
        assert isinstance(baseurl, str)
        assert isinstance(hp, unicode)
        
        p = os.path.join(self.localpath, hp).encode(sys.getfilesystemencoding() or 'utf-8')
        if os.path.exists(p):
            return open(p).read()

        url=urllib.basejoin(baseurl, urllib.quote(hp.encode('utf-8')))
        log.info("fetching %r" % (url,))

        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', 'mwlib')]
        try:
            d = opener.open(url).read()
            log.info("got image:", url)
        except urllib2.HTTPError, err:
            log.error("%s - while fetching %r" % (err,url))
            return            
        return d
    
    def clear(self):
         if self.tmpdir:
             log.info('removing %r' % self.tmpdir)
             shutil.rmtree(self.tmpdir, ignore_errors=True)
    

def normname(name):
    name = name.strip().replace("_", " ")
    name = name[:1].upper()+name[1:]
    return name
        
                 
class NetDB(object):
    redirect_rex = re.compile(r'^#Redirect:?\s*?\[\[(?P<redirect>.*?)\]\]', re.IGNORECASE)

    def __init__(self, pagename, imagedescription=None, templateurls=None, templateblacklist=None):
        self.pagename = pagename.replace("%", "%%").replace("@TITLE@", "%(NAME)s").replace("@REVISION@", "%(REVISION)s")

        self.templateurls = [x.replace("%", "%%").replace("@TITLE@", "%(NAME)s") for x in templateurls]

        if imagedescription is None:
            self.imagedescription = pagename.replace("%", "%%").replace("@TITLE@", "Image:%(NAME)s")
        else:
            self.imagedescription = imagedescription.replace("%", "%%").replace("@TITLE@", "%(NAME)s")
            
        if templateblacklist:
            self.templateblacklist = self._readTemplateBlacklist(templateblacklist)
        else:
            self.templateblacklist = []

        #self.pagename = "http://mw/index.php?title=%(NAME)s&action=raw&oldid=%(REVISION)s"
        #self.imagedescription = "http://mw/index.php?title=Image:%(NAME)s&action=raw"
        
        self.pages = {}
        
    def _getpage(self, url, expectedContentType='text/x-wiki'):
        try:
            return self.pages[url]
        except KeyError:
            pass
        
        stime=time.time()
        response = urllib.urlopen(url)
        data = response.read()
        log.info('fetched %r in %ss' % (url, time.time()-stime))

        if expectedContentType:
            ct = response.info().gettype()
            if ct != expectedContentType:
                log.warn('Skipping page %r with content-type %r (%r was expected). Skipping.'\
                        % (url, ct, expectedContentType))
                return None
        
        self.pages[url] = data
        return data

    def _readTemplateBlacklist(self,templateblacklist):
        if not templateblacklist:
            return []
        try:
            content = urllib.urlopen("%s?action=raw" % templateblacklist).read()
            return [template.lower().strip() for template in re.findall('\* *\[\[.*?:(.*?)\]\]', content)]
        except: # fixme: more sensible error handling...
            log.error('Error fetching template blacklist from url:', templateblacklist)
            return []
        
    def _dummy(self, *args, **kwargs):
        pass
    
    startCache = _dummy

    def getURL(self, title, revision=None):        
        name = urllib.quote(title.replace(" ", "_").encode('utf8'))
        if revision is None:
            return self.pagename % dict(NAME=name, REVISION='0')
        else:
            return self.pagename % dict(NAME=name, REVISION=revision)
    
    def title2db(self, title):
        assert isinstance(title, unicode), 'title must be of type unicode'
        return title.encode('utf-8')

    def db2title(self, dbtitle):
        assert isinstance(dbtitle, str), 'dbtitle must be of type str'
        return unicode(dbtitle, 'utf-8')

    def getImageDescription(self, title):
        NAME = urllib.quote(title.replace(" ", "_").encode('utf8'))
        url = self.imagedescription % dict(NAME=NAME)
        return self._getpage(url)

    def getImageMetaInfos(self, imgname):
        return {}

    def getTemplate(self, name, followRedirects=False):
        if ":" in name:
            name = name.split(':', 1)[1]

        
        if name.lower() in self.templateblacklist:
            log.info("ignoring blacklisted template:" , repr(name))
            return None
        name = urllib.quote(name.replace(" ", "_").encode('utf8'))
        for u in self.templateurls:
            url = u % dict(NAME=name)
            print "Trying", url
            c=self._getpage(url)
            if c:
                log.info("got content from", url)
                res=unicode(c, 'utf8')
                mo = self.redirect_rex.search(res)
                if mo:
                    redirect = mo.group('redirect')
                    redirect = normname(redirect.split("|", 1)[0].split("#", 1)[0])
                    return self.getTemplate(redirect)
                return res




        #return self.getRawArticle(u'Template:%s' % name)

    def getRawArticle(self, title, revision=None):
        r = self._getpage(self.getURL(title, revision=revision))
        if r is None:
            return None
        return unicode(r, 'utf8')
    
    def getRedirect(self, title):
        return u""

    def getParsedArticle(self, title):
        raw = self.getRawArticle(title)
        if raw is None:
            return None
        a = uparser.parseString(title=title, raw=raw, wikidb=self)
        return a

    def getEditors(self, title):
        return []

class Overlay(NetDB):
    def __init__(self, wikidb, templates):
        self.__dict__.update(wikidb.__dict__)
        self.overlay_templates = templates
        
    def getTemplate(self, name, followRedirects=False):
        try:
            return self.overlay_templates[name]
        except KeyError:
            pass
        
        return super(Overlay, self).getTemplate(name, followRedirects=followRedirects)
