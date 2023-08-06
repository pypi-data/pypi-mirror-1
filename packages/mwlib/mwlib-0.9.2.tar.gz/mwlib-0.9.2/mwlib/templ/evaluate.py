
# Copyright (c) 2007-2008 PediaPress GmbH
# See README.txt for additional licensing information.

from mwlib.templ import magics, log, DEBUG
from mwlib.templ import parser

recursion_count = 0

class TemplateRecursion(Exception): pass

def flatten(node, expander, variables, res):
    t=type(node)
    if t is unicode or t is str:
        res.append(node)
        return True

    global recursion_count

    if recursion_count>50:
        raise TemplateRecursion()
    
    
    recursion_count += 1
    try:
        before = variables.count
        oldlen = len(res)
        try:
            if t is list or t is tuple:
                for x in node:
                    flatten(x, expander, variables, res)
            else:
                node.flatten(expander, variables, res)
        except TemplateRecursion:
            if recursion_count > 2:
                raise
            del res[oldlen:]
            log.warn("template recursion error ignored")
        after = variables.count
        return before==after
    finally:
        recursion_count -= 1
        
        
class MemoryLimitError(Exception):
    pass


def equalsplit(node):
    if isinstance(node, basestring):
        if '=' in node:
            return node.split('=', 1)
        else:
            return None, node

    try:
        idx = node.index(u'=')
    except ValueError:
        return None, node

    return node[:idx], node[idx+1:]

    
def equalsplit_25(node):
    if isinstance(node, basestring):
        if '=' in node:
            return node.split('=', 1)
        else:
            return None, node

    try:
        idx = list(node).index(u'=')
    except ValueError:
        return None, node

    return node[:idx], node[idx+1:]
    
if not hasattr(tuple, 'index'):
    equalsplit = equalsplit_25

class ArgumentList(object):
    def __init__(self, args=tuple(), expander=None, variables=None):
        self.args = tuple(args)
        

        assert expander is not None
        #assert variables is not None
        
        self.expander = expander
        self.variables = variables
        self.varcount = 1
        self.varnum = 0
        
        self.namedargs = {}
        self.count = 0
            
    def __len__(self):
        self.count += 1
        return len(self.args)

    def __getitem__(self, n):
        self.count += 1
        return self.get(n, None) or u''
        
    def get(self, n, default):
        self.count += 1
        if isinstance(n, (int, long)):
            try:
                a=self.args[n]
            except IndexError:
                return default
            if isinstance(a, unicode):
                return a.strip()
            tmp = []
            flatten(a, self.expander, self.variables, tmp)
            _insert_implicit_newlines(tmp)
            tmp = u"".join(tmp).strip()
            if len(tmp)>256*1024:
                raise MemoryLimitError("template argument too long: %s bytes" % len(tmp))
            # FIXME: cache value ???
            return tmp

        assert isinstance(n, basestring), "expected int or string"

        if n not in self.namedargs:
            while self.varnum < len(self.args):
                arg = self.args[self.varnum]
                self.varnum += 1

                name, val = equalsplit(arg)
                if name is not None:
                    tmp = []
                    flatten(name, self.expander, self.variables, tmp)
                    _insert_implicit_newlines(tmp)
                    name = u"".join(tmp).strip()
                else:
                    name = str(self.varcount)
                    self.varcount+=1
                
                self.namedargs[name] = val
                
                if n==name:
                    break

        try:
            val = self.namedargs[n]
            if isinstance(val, unicode):
                return val
        except KeyError:
            return default

        tmp = []
        flatten(val, self.expander, self.variables, tmp)
        _insert_implicit_newlines(tmp)
        tmp=u"".join(tmp).strip()
        self.namedargs[n] = tmp
        return tmp
    
def is_implicit_newline(raw):
    """should we add a newline to templates starting with *, #, :, ;, {|
    see: http://meta.wikimedia.org/wiki/Help:Newlines_and_spaces#Automatic_newline_at_the_start
    """
    sw = raw.startswith
    for x in ('*', '#', ':', ';', '{|'):
        if sw(x):
            return True
    return False 

from mwlib.templ.marks import mark, mark_start, mark_end, mark_maybe_newline, maybe_newline, dummy_mark

def _insert_implicit_newlines(res, maybe_newline=maybe_newline):
    # do not pass the second argument
    res.append(dummy_mark)
    res.append(dummy_mark)
    for i, p in enumerate(res):
        if p is maybe_newline:
            s1 = res[i+1]
            s2 = res[i+2]
            if isinstance(s1, mark):
                continue
            if len(s1)>=2:
                if is_implicit_newline(s1):
                    res[i] = '\n'
            else:
                if is_implicit_newline(''.join([s1, s2])):
                    res[i] = '\n'
    del res[-2:]
    
class Expander(object):
    def __init__(self, txt, pagename="", wikidb=None):
        assert wikidb is not None, "must supply wikidb argument in Expander.__init__"
        self.db = wikidb
        self.resolver = magics.MagicResolver(pagename=pagename)
        self.resolver.wikidb = wikidb

        self.parsed = parser.parse(txt)
        #show(self.parsed)
        self.parsedTemplateCache = {}
        
    def getParsedTemplate(self, name):
        if name.startswith("[[") or "|" in name:
            return None
        try:
            return self.parsedTemplateCache[name]
        except KeyError:
            pass

        if name.startswith(":"):
            log.info("including article")
            raw = self.db.getRawArticle(name[1:])
        else:
            raw = self.db.getTemplate(name, True)
        
        if raw is None:
            log.warn("no template", repr(name))
            res = None
        else:
            log.info("parsing template", repr(name))
            res = parser.parse(raw)
            if DEBUG:
                print "TEMPLATE:", name, repr(raw)
                #res.show()
                
        self.parsedTemplateCache[name] = res
        return res
            
        
    def expandTemplates(self):
        res = []
        flatten(self.parsed, self, ArgumentList(expander=self), res)
        _insert_implicit_newlines(res)
        return u"".join(res)
