
# Copyright (c) 2007-2009 PediaPress GmbH
# See README.txt for additional licensing information.

import re

onlyincluderx = re.compile("<onlyinclude>(.*?)</onlyinclude>", re.DOTALL | re.IGNORECASE)
commentrx = re.compile(r"(\n *)?<!--.*?-->( *\n)?", re.DOTALL)
noincluderx1 = re.compile("<noinclude>.*?</noinclude>", re.DOTALL | re.IGNORECASE)
noincluderx2 = re.compile("<noinclude>.*", re.DOTALL | re.IGNORECASE)

def remove_comments(txt):
    def repl(m):
        #print "M:", repr(txt[m.start():m.end()])
        if txt[m.start()]=='\n' and txt[m.end()-1]=='\n':
            return '\n'
        return (m.group(1) or "")+(m.group(2) or "")
    return commentrx.sub(repl, txt)

def preprocess(txt):
    #txt=txt.replace("\t", " ")
    txt=remove_comments(txt)

    txt = noincluderx1.sub(u'', txt)
    txt = noincluderx2.sub(u'', txt)
    
    if "<onlyinclude>" in txt:
        # if onlyinclude tags are used, only use text between those tags. template 'legend' is a example
        txt = "".join(onlyincluderx.findall(txt))
        
    return txt
