#! /usr/bin/env python

# Copyright (c) 2007-2009 PediaPress GmbH
# See README.txt for additional licensing information.

"""client for mediawiki's api.php using twisted"""

import os
import sys
import urlparse

from mwlib import metabook, utils, nshandling

from mwlib.net import mwapi
from mwlib.net.pod import PODClient

from mwlib import myjson as json

from twisted.python import failure, log
from twisted.web import client 
from twisted.internet import reactor, defer

class shared_progress(object):
    status=None
    last_percent=0.0
    
    def __init__(self, status=None):
        self.key2count = {}
        self.status=status
        
    def report(self):
        isatty = getattr(sys.stdout, "isatty", None)
        done, total = self.get_count()
        if not total:
            total = 1
            
        
        if total < 50:
            percent = done / 5.0
        else:
            percent =  100.0*done / total

        if percent<self.last_percent:
            percent=self.last_percent
        else:
            self.last_percent=percent
            
        if isatty and isatty():
            msg = "%s/%s %.2f" % (done, total, percent)
            sys.stdout.write("\x1b[K"+msg+"\r")
            sys.stdout.flush()

        if self.status:
            self.status(status="fetching", progress=percent)

    def set_count(self, key, done, total):
        self.key2count[key] = (done, total) 
        self.report()
        
    def get_count(self):
        done  = 0
        total = 0
        for (d, t) in self.key2count.values():
            done+=d
            total+=t
        return done, total
    
class fsoutput(object):
    def __init__(self, path):
        self.path = os.path.abspath(path)
        assert not os.path.exists(self.path)
        os.makedirs(os.path.join(self.path, "images"))
        self.revfile = open(os.path.join(self.path, "revisions-1.txt"), "wb")
        # self.revfile.write("\n -*- mode: wikipedia -*-\n")
        self.seen = set()
        self.imgcount = 0
        
    def close(self):
        self.revfile.close()
        self.revfile = None
        
        
    def get_imagepath(self, title):
        p = os.path.join(self.path, "images", "%s" % (utils.fsescape(title),))
        self.imgcount+=1
        return p
        
    def dump_json(self, **kw):
        for k, v in kw.items():
            p = os.path.join(self.path, k+".json")
            json.dump(v, open(p, "wb"), indent=4, sort_keys=True)
            
                
    def write_siteinfo(self, siteinfo):
        self.dump_json(siteinfo=siteinfo)

    def write_excluded(self, excluded):
        self.dump_json(excluded=excluded)

    def write_licenses(self, licenses):
        self.dump_json(licenses=licenses)
        
    def write_pages(self, data):
        pages = data.get("pages", {}).values()
        for p in pages:
            
            title = p.get("title")
            ns = p.get("ns")
            revisions = p.get("revisions")
            
            if revisions is None:
                continue

            tmp = []
            for x in revisions:
                x = x.copy()
                x["*"] = len(x["*"])
                tmp.append(x)
            
            for r in revisions:
                revid = r.get("revid")
                txt = r["*"]
                if revid not in self.seen:
                    rev = dict(title=title, ns=ns)
                    if revid is not None:
                        self.seen.add(revid)
                        rev["revid"] = revid

                    header = "\n --page-- %s\n" % json.dumps(rev, sort_keys=True)
                    self.revfile.write(header)
                    self.revfile.write(txt.encode("utf-8"))
                # else:    
                #     print "fsoutput: skipping duplicate:", dict(revid=revid, title=title)

    def write_edits(self, edits):
        self.dump_json(edits=edits)

    def write_redirects(self, redirects):
        self.dump_json(redirects=redirects)
        
                        
def splitblocks(lst, limit):
    """Split list lst in blocks of max. limit entries. Return list of blocks."""

    res = []
    start = 0
    while start<len(lst):
        res.append(lst[start:start+limit])
        start+=limit
    return res

def getblock(lst, limit):
    """Return first limit entries from list lst and remove them from the list"""

    r = lst[-limit:]
    del lst[-limit:]
    return r


class fetcher(object):
    def __init__(self, api, fsout, pages, licenses,
                 status=None,
                 progress=None,
                 print_template_pattern=None,
                 template_exclusion_category=None,
                 imagesize=800):
        self.result = defer.Deferred()
        
        self._stopped = False 
        self.fatal_error = "stopped by signal"
        
        self.api = api
        self.api.report = self.report
        self.apipool = mwapi.pool()
        self.apipool.multi.key2val[api.baseurl] = api
        
        self.fsout = fsout
        self.licenses = licenses
        self.status = status
        self.progress = progress or shared_progress(status=status)

        self.template_exclusion_category = template_exclusion_category
        self.print_template_pattern = print_template_pattern

        self.imagesize = imagesize

        if self.print_template_pattern:
            self.make_print_template = utils.get_print_template_maker(self.print_template_pattern)
        else:
            self.make_print_template = None
            
        self._nshandler = None
        
        self.redirects = {}
        self.cat2members = {}
        
        self.count_total = 0
        self.count_done = 0

        self.title2latest = {}
    
        self.edits = []
        self.lambda_todo = []
        self.pages_todo = []
        self.revids_todo = []
        self.imageinfo_todo = []
        self.imagedescription_todo = {} # base path -> list
        
        self.scheduled = set()

        self.simult = mwapi.multiplier()
        
        self._refcall(lambda:self.get_siteinfo_for(self.api)
                      .addCallback(self._cb_siteinfo)
                      .addErrback(self.make_die_fun("could not get siteinfo")))
                      
        titles, revids = self._split_titles_revids(pages)
        

        limit = self.api.api_request_limit
        dl = []

        def fetch_used(name, lst):            
            for bl in splitblocks(lst, limit):
                kw = {name:bl}
                dl.append(self._refcall(lambda: self.api.fetch_used(**kw).addCallback(self._cb_used)))

        
        fetch_used("titles", titles)
        fetch_used("revids", revids)


        self._refcall(lambda: defer.DeferredList(dl).addCallbacks(self._cb_finish_used, self._cb_finish_used))
        
            
        self.report()
        self.dispatch()

    def get_siteinfo_for(self, m):
        return self.simult.get(m.baseurl, m.get_siteinfo)
                                
    def _split_titles_revids(self, pages):
        titles = set()
        revids = set()        
           
        for p in pages:
            if p[1] is not None:
                revids.add(p[1])
            else:
                titles.add(p[0])
                
        titles = list(titles)
        titles.sort()

        revids = list(revids)
        revids.sort()
        return titles, revids

    def _cb_finish_used(self, data):
        for title, rev in self.title2latest.items():
             self._refcall(lambda: self.api.get_edits(title, rev).addCallback(self._got_edits))
        self.title2latest = {}
        
    def _cb_siteinfo(self, siteinfo):
        self.fsout.write_siteinfo(siteinfo)
        self.nshandler = nshandling.nshandler(siteinfo)
        if self.template_exclusion_category:
            ns, partial, fqname = self.nshandler.splitname(self.template_exclusion_category, 14)
            if ns!=14:
                print "bad category name:", repr(self.template_exclusion_category)
            # else:
            #     self._refcall(lambda: self.api.get_categorymembers(fqname).addCallback(self._cb_excluded_category))
            
    def _cb_excluded_category(self, data):
        members = data.get("categorymembers")
        self.fsout.write_excluded(members)
        
        
        
    def report(self):
            
        
        qc = self.api.qccount

        limit = self.api.api_request_limit
        jt = self.count_total+len(self.pages_todo)//limit+len(self.revids_todo)//limit
        jt += len(self.title2latest)


        if self.progress:
            self.progress.set_count(self, self.count_done+qc,  jt+qc)
            return
        
                                    
        

        
        msg = "%s/%s/%s jobs -- %s/%s running" % (self.count_done+qc, self.count_total+qc, jt+qc, self.api.num_running, self.api.max_connections)

        if jt < 10:
            progress = self.count_done
        else:
            progress =  100.0*self.count_done /  jt
            
        if self.status:
            self.status(status="fetching", progress=progress)
            
        isatty = getattr(sys.stdout, "isatty", None)
        if isatty and isatty():
            sys.stdout.write("\x1b[K"+msg+"\r")
            sys.stdout.flush()
            
    def _got_edits(self, data):
        edits = data.get("pages").values()
        self.edits.extend(edits)

    def _add_catmember(self, title, entry):
        try:
            self.cat2members[title].append(entry)
        except KeyError:
            self.cat2members[title] = [entry]
            
        
    def _handle_categories(self, data):
        pages = data.get("pages", {}).values()
        for p in pages:
            categories = p.get("categories")
            if not categories:
                continue
            
            e = dict(title = p.get("title"), ns = p.get("ns"), pageid=p.get("pageid"))

            for c in categories:
                cattitle = c.get("title")
                if cattitle:
                    self._add_catmember(cattitle, e)
                
    def _got_pages(self, data):
        r = data.get("redirects", [])
        self._update_redirects(r)
        self._handle_categories(data)
        self.fsout.write_pages(data)
        return data

    def _extract_attribute(self, lst, attr):
        res = []
        for x in lst:
            t = x.get(attr)
            if t:
                res.append(t)
        
        return res
    def _extract_title(self, lst):
        return self._extract_attribute(lst, "title")

    def _update_redirects(self, lst):
        for x in lst:
            t = x.get("to")
            f = x.get("from")
            if t and f:
                self.redirects[f]=t
                
    def _cb_used(self, used):
        self._update_redirects(used.get("redirects", []))        
        
        pages = used.get("pages", {}).values()
        
        revids = set()
        for p in pages:
            tmp = self._extract_attribute(p.get("revisions", []), "revid")
            if tmp:
                latest = max(tmp)
                title = p.get("title", None)
                old = self.title2latest.get(title, 0)
                self.title2latest[title] = max(old, latest)    
                
            revids.update(tmp)
        
        templates = set()
        images = set()
        for p in pages:
            images.update(self._extract_title(p.get("images", [])))
            templates.update(self._extract_title(p.get("templates", [])))

        for i in images:
            if i not in self.scheduled:
                self.imageinfo_todo.append(i)
                self.scheduled.add(i)
                
        for r in revids:
            if r not in self.scheduled:
                self.revids_todo.append(r)
                self.scheduled.add(r)
                
        for t in templates:
            if t not in self.scheduled:
                self.pages_todo.append(t)
                self.scheduled.add(t)

            if self.print_template_pattern is not None and ":" in t:
                t = self.make_print_template(t)                
                if t not in self.scheduled:
                    self.pages_todo.append(t)
                    self.scheduled.add(t)

    def _download_image(self, url, title):
        path = self.fsout.get_imagepath(title)
        tmp = (path+u'\xb7').encode("utf-8")
        def done(val):
            os.rename(tmp, path)
            return val
        
        return client.downloadPage(str(url), tmp).addCallback(done)
        
        
    def _cb_imageinfo(self, data):
        # print "data:", data
        infos = data.get("pages", {}).values()
        # print infos[0]
        new_basepaths = set()
        
        for i in infos:
            title = i.get("title")
            
            ii = i.get("imageinfo", [])
            if not ii:
                continue
            ii = ii[0]
            thumburl = ii.get("thumburl", None)
            # FIXME limit number of parallel downloads
            if thumburl:
                # FIXME: add Callback that checks correct file size
                if thumburl.startswith('/'):
                    thumburl = urlparse.urljoin(self.api.baseurl, thumburl)
                self._refcall(lambda: self._download_image(thumburl, title))

                descriptionurl = ii.get("descriptionurl", "")
                if "/" in descriptionurl:
                    path, localname = descriptionurl.rsplit("/", 1)
                    t = (title, descriptionurl)
                    if path in self.imagedescription_todo:
                        self.imagedescription_todo[path].append(t)
                    else:
                        new_basepaths.add(path)
                        self.imagedescription_todo[path] = [t]
                        
        for path in new_basepaths:
            self._refcall(lambda: self._get_mwapi_for_path(path).addCallback(self._cb_got_api, path))



    def _get_nshandler(self):
        if self._nshandler is not None:
            return self._nshandler
        return nshandling.get_nshandler_for_lang('en') # FIXME

    def _set_nshandler(self, nshandler):
        self._nshandler = nshandler

    nshandler = property(_get_nshandler, _set_nshandler)

    def _cb_image_edits(self, data):
        edits = data.get("pages").values()

        local_nsname = self.nshandler.get_nsname_by_number(6)
        
        # change title prefix to make them look like local pages
        for e in edits:
            title = e.get("title")
            prefix, partial = title.split(":", 1)
            e["title"] = "%s:%s" % (local_nsname, partial)

        self.edits.extend(edits)

    def _cb_image_contents(self, data):
        local_nsname = self.nshandler.get_nsname_by_number(6)
        
        pages = data.get("pages", {}).values()
        # change title prefix to make them look like local pages
        for p in pages:
            title = p.get("title")
            prefix, partial = title.split(":", 1)
            p["title"] = "%s:%s" % (local_nsname, partial)

            revisions = p.get("revisions", [])
            # the revision id's could clash with some local ids. remove them.
            for r in revisions:
                try:
                    del r["revid"]
                except KeyError:
                    pass
            
            
        # XXX do we also need to handle redirects here?
        self.fsout.write_pages(data)
    
    def _cb_got_api(self, api, path):
        assert api
        todo = self.imagedescription_todo[path]
        del self.imagedescription_todo[path]
        
        titles = set([x[0] for x in todo])
        # "-d-" is just some prefix to make the names here not clash with local names
        titles = [t for t in titles if "-d-"+t not in self.scheduled]
        self.scheduled.update(["-d-"+x for x in titles])
        if not titles:
            return
        
        def got_siteinfo(siteinfo):
            ns = nshandling.nshandler(siteinfo)
            nsname = ns.get_nsname_by_number(6)
            
            local_names=[]
            for x in titles:
                partial = x.split(":", 1)[1]
                local_names.append("%s:%s" % (nsname, partial))


            for bl in splitblocks(local_names, api.api_request_limit):
                self.lambda_todo.append(lambda bl=bl: api.fetch_pages(titles=bl).addCallback(self._cb_image_contents))

            for k in local_names:
                self.lambda_todo.append(lambda title=k: api.get_edits(title, None).addCallback(self._cb_image_edits))
        
        # print "got api for", repr(path), len(todo)
        return self.get_siteinfo_for(api).addCallback(got_siteinfo)
        
            
    def _get_mwapi_for_path(self, path):
        urls = mwapi.guess_api_urls(path)
        if not urls:
            return defer.fail("cannot guess api url for %r" % (path,))

        return self.apipool.try_api_urls(urls)
            
    def dispatch(self):
        if self._stopped:
            return
        
        limit = self.api.api_request_limit

        def doit(name, lst):
            while lst and self.api.idle():
                bl = getblock(lst, limit)
                self.scheduled.update(bl)
                kw = {name:bl}
                self._refcall(lambda: self.api.fetch_pages(**kw).addCallback(self._got_pages))

        while self.imageinfo_todo and self.api.idle():
            bl = getblock(self.imageinfo_todo, limit)
            self.scheduled.update(bl)
            self._refcall(lambda: self.api.fetch_imageinfo(titles=bl, iiurlwidth=self.imagesize).addCallback(self._cb_imageinfo))
            
        doit("revids", self.revids_todo)
        doit("titles", self.pages_todo)

        while self.lambda_todo:
            self._refcall(self.lambda_todo.pop())

        self.report()
        
        if self.count_done==self.count_total:
            self.finish()
            self.fatal_error = None
            print
            self._stop_reactor()

    def _stop_reactor(self):
        
        if self._stopped:
            return
        
        if self.fatal_error:
            if isinstance(self.fatal_error, basestring):
                self.result.errback(RuntimeError(self.fatal_error))
            else:
                self.result.errback(self.fatal_error)
        else:
            self.result.callback(None)
            
        self._stopped = True

    def _compute_excluded(self):
        if self.template_exclusion_category:
            ns, partial, fqname = self.nshandler.splitname(self.template_exclusion_category, 14)
            excluded = self.cat2members.get(fqname)
            if excluded:
                self.fsout.write_excluded(excluded)
            
    def finish(self):
        self._compute_excluded()
        self.fsout.write_edits(self.edits)
        self.fsout.write_redirects(self.redirects)
        self.fsout.write_licenses(self.licenses)
        self.fsout.close()
        
    def _refcall(self, fun):
        """Increment refcount, schedule call of fun (returns Deferred)
        decrement refcount after fun has finished.
        """

        self._incref()
        try:
            d=fun()
            assert isinstance(d, defer.Deferred), "got %r" % (d,)
        except:
            self._decref(None)
            print "function failed"
            raise
        return d.addCallbacks(self._decref, self._decref)
        
    def _incref(self):
        self.count_total += 1
        self.report()
        
    def _decref(self, val):
        self.count_done += 1
        reactor.callLater(0.0, self.dispatch)
        if isinstance(val, failure.Failure):
            log.err(val)

    def make_die_fun(self, reason):
        def fatal(val):
            self.fatal_error = reason
            self._stop_reactor()
            print "fatal: %s [%s]" % (reason, val)        
            
        return fatal
    
def pages_from_metabook(mb):
    articles = mb.articles()
    pages = [(x.title, x.revision) for x in articles]
    return pages
