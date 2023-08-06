#! /usr/bin/env python

# Copyright (c) 2007-2009 PediaPress GmbH
# See README.txt for additional licensing information.

import sys

from mwlib.templ import log

from mwlib.templ.nodes import Node, Variable, Template, show
from mwlib.templ.scanner import tokenize
from mwlib.templ.parser import parse, Parser
from mwlib.templ.evaluate import flatten, Expander, ArgumentList
from mwlib.templ.misc import DictDB, expandstr


def get_templates(raw):
    used = set()
    todo = [parse(raw)]
    while todo:
        n = todo.pop()
        if isinstance(n, basestring):
            continue
        
        if isinstance(n, Template) and isinstance(n[0], basestring):
            used.add(n[0])
            
        todo.extend(n)
        
    return used

def find_template(raw, name):
    """Return Template node with given name or None if there is no such template"""
    
    todo = [parse(raw)]
    while todo:
        n = todo.pop()
        if isinstance(n, basestring):
            continue
        if isinstance(n, Template) and isinstance(n[0], basestring):
            if n[0] == name:
                return n
        todo.extend(n)

def get_template_args(template, expander):
    """Return ArgumentList for given template"""
    
    return ArgumentList(template[1],
        expander=expander,
        variables=ArgumentList(expander=expander),
    )
    

if __name__=="__main__":
    d=unicode(open(sys.argv[1]).read(), 'utf8')
    e = Expander(d)
    print e.expandTemplates()
