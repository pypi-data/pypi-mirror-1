#! /usr/bin/env py.test
# -*- coding: utf-8 -*-
# Copyright (c) 2007-2008 PediaPress GmbH
# See README.txt for additional licensing information.

import sys

from mwlib.advtree import buildAdvancedTree
from mwlib import parser
from mwlib.treecleaner import TreeCleaner, _all, _any
from mwlib.advtree import (Article, ArticleLink, Blockquote, BreakingReturn, CategoryLink, Cell, Center, Chapter,
                     Cite, Code, DefinitionList, Div, Emphasized, Gallery, HorizontalRule, ImageLink, InterwikiLink, Item,
                     ItemList, LangLink, Link, Math, NamedURL, NamespaceLink, Paragraph, PreFormatted,
                     Reference, ReferenceList, Row, Section, Source, SpecialLink, Table, Text, Underline,
                     URL)

from mwlib.xfail import xfail

def _treesanity(r):
    "check that parents match their children"
    for c in r.allchildren():
        if c.parent:
            assert c in c.parent.children
            assert len([x for x in c.parent.children if x is c]) == 1
        for cc in c:
            assert cc.parent
            assert cc.parent is c
            

def getTreeFromMarkup(raw):
    from mwlib.dummydb import DummyDB
    from mwlib.uparser import parseString
    return parseString(title="Test", raw=raw, wikidb=DummyDB())
    
def cleanMarkup(raw):
    tree  = getTreeFromMarkup(raw)
    buildAdvancedTree(tree)
    tc = TreeCleaner(tree, save_reports=True)
    tc.cleanAll(skipMethods=[])
    reports = tc.getReports()
    return (tree, reports)

def cleanMarkupSingle(raw, cleanerMethod):
    tree  = getTreeFromMarkup(raw)
    buildAdvancedTree(tree)
    tc = TreeCleaner(tree, save_reports=True)
    tc.clean([cleanerMethod])
    reports = tc.getReports()
    return (tree, reports)
    

def showTree(tree):
    parser.show(sys.stderr, tree, 0)
    

def test_fixLists():
    raw = r"""
para

* list item 1
* list item 2
** list item 2.1
* list item 3

* list 2 item 1
* list 2 item 2

para

* list 3
    """
    tree, reports = cleanMarkup(raw)
    lists = tree.getChildNodesByClass(ItemList)
    for li in lists:
        assert _all([p.__class__ != Paragraph for p in li.getParents()])
    _treesanity(tree)   

def test_fixLists2():
    raw = r"""
* list item 1
* list item 2
some text in the same paragraph
    """    
    # cleaner should do nothing
    tree, reports = cleanMarkup(raw)
    lists = tree.getChildNodesByClass(ItemList)
    li = lists[0]
    assert li.parent.__class__ == Paragraph
    assert Text in [sib.__class__ for sib in li.siblings]


def test_fixLists3():
    raw = r"""
* ul1
* ul2
# ol1
# ol2
"""
    tree, reports = cleanMarkup(raw)
    assert len(tree.children) == 2 # 2 itemlists as only children of article
    assert _all( [ c.__class__ == ItemList for c in tree.children])
    

def test_childlessNodes():
    raw = r"""
blub
    
<source></source>

*

<div></div>

<u></u>
    """
    tree, reports = cleanMarkup(raw)
    assert len(tree.children) == 1 #assert only the 'blub' paragraph is left and the rest removed
    assert tree.children[0].__class__ == Paragraph  


def test_removeLangLinks():
    raw = r"""
bla blub [[it:blub]] bla

[[de:Blub]]
[[en:Blub]]
[[es:Blub]]
"""
    tree, reports = cleanMarkup(raw)
    assert len(tree.children) == 1
    assert tree.children[0].__class__ == Paragraph
    assert tree.children[0].children[1].__class__ == LangLink


def test_removeCriticalTables():
    raw = r'''
{| class="navbox"
|-
| bla
| blub
|}

blub
'''    
    tree, reports = cleanMarkup(raw)
    assert len(tree.getChildNodesByClass(Table)) == 0


def test_fixTableColspans():
    raw = r'''
{|
|-
| colspan="5" | bla
|-
| bla
| blub
|}
    '''
    tree, reports = cleanMarkup(raw)
    t = tree.getChildNodesByClass(Table)[0]
    cell = t.children[0].children[0]
    assert cell.colspan == 2

def test_removeBrokenChildren():
    raw = r'''
<ref>
 preformatted text
</ref>
    '''
    
    tree, reports = cleanMarkup(raw)
    assert len(tree.getChildNodesByClass(PreFormatted)) == 0


def test_fixNesting1():
    raw = r'''
 preformatted text <source>some source text</source> some text after the source node    
    '''
    tree, reports = cleanMarkup(raw)
    source_node = tree.getChildNodesByClass(Source)[0]
    assert not _any([p.__class__ == PreFormatted for p in source_node.getParents()]) 
    p = tree.getChildNodesByClass(Paragraph)[0]
    assert p.children[0].__class__ == PreFormatted and p.children[0].children[0].caption.find('preformatted text') > -1
    assert p.children[1].__class__ == Source and len(p.children[1].children) > 0
    assert p.children[2].__class__ == PreFormatted and p.children[2].children[0].caption.find('some text') > -1

def test_fixNesting2():
    raw = r'''
<div><div>
* bla
* blub
</div></div>
    '''
    tree, reports = cleanMarkup(raw)
    list_node = tree.getChildNodesByClass(ItemList)[0]
    assert not _any([p.__class__ == Div for p in list_node.getParents()])

def test_fixNesting3():
    raw = r'''
<strike>
para 1

para 2
</strike>
    '''

    tree, reports = cleanMarkup(raw)
    paras = tree.getChildNodesByClass(Paragraph)
    for para in paras:
        assert not para.getChildNodesByClass(Paragraph)

def test_fixNesting4():
    raw = """
<strike>

<div>
 indented para 1

regular para

 indented para 2

</div>

</strike>
"""

    tree = getTreeFromMarkup(raw)
    showTree(tree)
    
    tree, reports = cleanMarkup(raw)
    showTree(tree)
    paras = tree.getChildNodesByClass(Paragraph)
    for para in paras:
        assert not para.getChildNodesByClass(Paragraph)
      
def test_fixNesting5():
    raw = """
<strike>
<div>

<div>

<div>
para 1
</div>

para 2
</div>

<div>
para 2
</div>

</div>
</strike>
    """

    tree, reports = cleanMarkup(raw)
    paras = tree.getChildNodesByClass(Paragraph)
    for para in paras:
        assert not para.getChildNodesByClass(Paragraph) 


def test_swapNodes():
    raw = r'''
<u><center>Text</center></u>
    '''
    tree, reports = cleanMarkup(raw)
    center_node= tree.getChildNodesByClass(Center)[0]
    assert not _any([p.__class__ == Underline for p in center_node.getParents()])

@xfail
def test_splitBigTableCells():
    '''
    Splitting big table cells can not properly be tested here.
    Testing needs to be done in the writers, since this test is writer
    specific and the output has to be verfied
    '''
    assert False
    

@xfail
def test_fixParagraphs():
    raw = r'''  ''' #FIXME: which markup results in paragraphs which are not properly nested with preceeding sections?
    tree, reports = cleanMarkup(raw)
    assert False


def test_cleanSectionCaptions():
    raw = r'''
==<center>centered heading</center>==    
    '''

    tree, reports = cleanMarkup(raw)
    section_node = tree.getChildNodesByClass(Section)[0]
    assert _all([p.__class__ != Center for p in section_node.children[0].getAllChildren()])

def test_cleanSectionCaptions2():
    raw = """=== ===
    bla
    """

    tree, reports = cleanMarkup(raw)
    assert len(tree.getChildNodesByClass(Section)) == 0

    
def numBR(tree):
    return len(tree.getChildNodesByClass(BreakingReturn))

def test_removebreakingreturnsInside():
    # remove BRs at the inside 'borders' of block nodes
    raw = '''
{|
|-
|<br/>blub<br/>
|text
|-
|<source></source><br/>text
| text
|-
|<br/><source></source><br/><br/>text
| text
|}
'''
    tree, reports = cleanMarkup(raw) # 1 & 2
    assert numBR(tree) == 0


def test_removebreakingreturnsOutside():
    # remove BRs at the outside 'borders' of block nodes
    raw = '''
<br/>

== section heading ==

<br/>

text

<br/>

<br/>

== section heading 2 ==

<br/><br/>

== section heading 3 ==
<br/>bla</br/>
'''

    tree, reports = cleanMarkup(raw)
    showTree(tree)
    assert numBR(tree) == 0


def test_removebreakingreturnsMultiple():
    # remove BRs at the outside 'borders' of block nodes
    raw = '''
paragraph

<br/>

<br/>

paragraph
'''

    tree, reports = cleanMarkup(raw) 
    assert numBR(tree) == 0


def test_removebreakingreturnsNoremove():
    raw = """
<br/>
<source>
<br/>dummy code line 1 <br/> next line of code <br/>  
</source>

<br/>
 <br/> bla <br/> blub

ordinary paragraph. inside <br/> tags should not be removed 
"""

    tree, reports = cleanMarkup(raw) 
    # the br tags inside the source tag are not converted to br nodes - they remain inside the text
    # the only br tags that should remain after cleaning are the ones inside the preformatted node
    assert numBR(tree) == 3

def test_preserveEmptyTextNodes():
    raw="""[[blub]] ''bla'' """
    tree, reports = cleanMarkup(raw) 
    p = tree.find(Paragraph)[0]
    assert isinstance(p.children[1], Text) and p.children[1].caption==' '

def test_gallery():
    raw ="""<gallery>
Image:There_Screenshot02.jpg|Activities include hoverboarding, with the ability to perform stunts such as dropping down from space
Image:Scenery.jpg|A wide pan over a seaside thatched-roof village
|Members can join and create interest groups
Image:Landmark02.jpg|There contains many landmarks, including a replica of New Orleans
Image:Emotes01.jpg|Avatars can display over 100 emotes
<!-- Deleted image removed: Image:Popoutemotes01.jpg|Avatars can display a wide variety of pop-out emotes -->
Image:Zona.jpg|Zona Island, a place where new members first log in.
Image:Hoverboat01.jpg|A member made vehicle. As an avatar users can paint and build a variety of items.
Image:|Zona Island, a place where new members first log in
<!-- Deleted image removed: Image:OldWaterinHole.jpg|The Old Waterin' Hole: a place where users can sit and chat while in a social club/bar-like environment. -->
</gallery>"""

    tree, reports = cleanMarkup(raw) 
    gallery = tree.find(Gallery)[0]
    assert len(gallery.children) == 6
