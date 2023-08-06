#! /usr/bin/env python
#! -*- coding:utf-8 -*-

# Copyright (c) 2007, PediaPress GmbH
# See README.txt for additional licensing information.

from mwlib import advtree

def isInline(img_node):
    if getattr(img_node, 'align', '').lower() == 'center' or \
           advtree.Center in [p.__class__ for p in img_node.getParents()]:
        return False
    is_inline = img_node.isInline()
    # override the isInline value if images are very small, or very large
    w = getattr(img_node, 'width', 100)
    if 0 <  w < 50: # images where no width is explicitly given in MW-markup, get width=0 by parser.
        is_inline = True
    if w > 150:
        is_inline = False
    return is_inline
