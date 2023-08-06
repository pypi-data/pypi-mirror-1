#! /usr/bin/env py.test

# Copyright (c) 2007-2008 PediaPress GmbH
# See README.txt for additional licensing information.

from mwlib import parser, expander, uparser
from mwlib.expander import DictDB

parse = uparser.simpleparse
    
def test_headings():
    r=parse(u"""
= 1 =
== 2 ==
= 3 =
""")
    
    sections = [x.children[0].asText().strip() for x in r.children if isinstance(x, parser.Section)]
    assert sections == [u"1", u"3"]


def test_style():
    r=parse(u"'''mainz'''")
    s=r.children[0].children[0]
    assert isinstance(s, parser.Style)
    assert s.caption == "'''"

def test_single_quote_after_style():
    """http://code.pediapress.com/wiki/ticket/20"""
    
    r=parse(u"''pp'''s")
    styles = r.find(parser.Style)
    assert len(styles)==1, "should be pp's"
    
    
    s=r.children[0].children[0]
    assert isinstance(s, parser.Style)
    assert s.caption == "'''"
    

def test_links_in_style():
    r=parse(u"'''[[mainz]]'''")
    s=r.children[0].children[0]
    assert isinstance(s, parser.Style)
    assert isinstance(s.children[0], parser.Link)
    


def test_parse_image_inline():
    #r=parse("[[Bild:flag of Italy.svg|30px]]")
    #img = [x for x in r.allchildren() if isinstance(x, parser.ImageLink)][0]
    #print "IMAGE:", img, img.isInline()

    r=parse(u'{| cellspacing="2" border="0" cellpadding="3" bgcolor="#EFEFFF" width="100%"\n|-\n| width="12%" bgcolor="#EEEEEE"| 9. Juli 2006\n| width="13%" bgcolor="#EEEEEE"| Berlin\n| width="20%" bgcolor="#EEEEEE"| [[Bild:flag of Italy.svg|30px]] \'\'\'Italien\'\'\'\n| width="3%" bgcolor="#EEEEEE"| \u2013\n| width="20%" bgcolor="#EEEEEE"| [[Bild:flag of France.svg|30px]] Frankreich\n| width="3%" bgcolor="#EEEEEE"|\n| width="25%" bgcolor="#EEEEEE"| [[Fu\xdfball-Weltmeisterschaft 2006/Finalrunde#Finale: Italien .E2.80.93 Frankreich 6:4 n. E..2C 1:1 n. V. .281:1.2C 1:1.29|6:4 n. E., (1:1, 1:1, 1:1)]]\n|}\n')
    images = r.find(parser.ImageLink)

    assert len(images)==2

    for i in images:
        print "-->Image:", i, i.isInline()


def test_parse_image_6():
    """http://code.pediapress.com/wiki/ticket/6"""
    r=parse("[[Bild:img.jpg|thumb|+some text]] [[Bild:img.jpg|thumb|some text]]")

    images = r.find(parser.ImageLink)
    assert len(images)==2
    print images
    assert images[0].isInline() == images[1].isInline()


def test_self_closing_nowiki():
    parse(u"<nowiki/>")
    parse(u"<nowiki  />")
    parse(u"<nowiki       />")
    parse(u"<NOWIKI>[. . .]</NOWIKI>")



def test_break_in_li():
    r=parse("<LI> foo\n\n\nbla")
    tagnode = r.find(parser.TagNode)[0]
    assert hasattr(tagnode, "starttext")
    assert hasattr(tagnode, "endtext")


def test_switch_default():

    db=DictDB(
        Bonn="""{{Infobox
|Bundesland         = Nordrhein-Westfalen
}}
""",
        Infobox="""{{#switch: {{{Bundesland}}}
        | Bremen = [[Bremen (Land)|Bremen]]
        | #default = [[{{{Bundesland|Bayern}}}]]
}}
""")

    te = expander.Expander(db.getRawArticle("Bonn"), pagename="thispage", wikidb=db)
    res = te.expandTemplates()

    
    print "EXPANDED:", repr(res)
    assert "Nordrhein-Westfalen" in res

def test_pipe_table():

    db=DictDB(Foo="""
bla
{{{ {{Pipe}}}
blubb
""",
                   Pipe="|")

    te = expander.Expander(db.getRawArticle("Foo"), pagename="thispage", wikidb=db)
    res = te.expandTemplates()

    
    print "EXPANDED:", repr(res)
    assert "bla" in res
    assert "blubb" in res

def test_pipe_begin_table():

    db=DictDB(Foo="""
bla
{{{Pipe}} |}
blubb
""",
              Pipe="|")

    te = expander.Expander(db.getRawArticle("Foo"), pagename="thispage", wikidb=db)
    res = te.expandTemplates()
    
    
    print "EXPANDED:", repr(res)
    assert "bla" in res
    assert "blubb" in res
    assert "{|" in res

def test_cell_parse_bug():
    """http://code.pediapress.com/wiki/ticket/17"""
    r=parse("""{|
|-
[[Image:bla.png|bla]]
|}""")
    print r
    
    images = r.find(parser.ImageLink)
    assert images

def test_table_not_eating():
    """internal parser error.
    http://code.pediapress.com/wiki/ticket/32
    http://code.pediapress.com/wiki/ticket/29    
"""
    uparser.simpleparse("""{|)
|10<sup>10<sup>100</sup></sup>||gsdfgsdfg
|}""")

def test_table_not_eating2():
    """internal parser error.
    http://code.pediapress.com/wiki/ticket/32
    http://code.pediapress.com/wiki/ticket/29    
"""
    uparser.simpleparse("""{| 
<tr><td>'''Birth&nbsp;name'''</td><td colspan="2">Alanis Nadine Morissette</td></tr><tr><td>'''Born'''</td>
|}
""")


def test_parse_comment():
    ex = """foo
<!-- comment --->
bar"""

    def check(node):
        paras = node.find(parser.Paragraph)
        assert len(paras)==1, 'expected exactly one paragraph node'
    
    check(parse(ex))
    check(parse(expander.expandstr(ex)))

def test_nowiki_entities():
    """http://code.pediapress.com/wiki/ticket/40"""
    node = parse("<nowiki>&amp;</nowiki>")
    txt = node.find(parser.Text)[0]
    assert txt.caption==u'&', "expected an ampersand"

def test_blockquote_with_newline():
    """http://code.pediapress.com/wiki/ticket/41"""
    node = parse("<blockquote>\nblockquoted</blockquote>").find(parser.Style)[0]
    print "STYLE:", node
    assert "blockquoted" in node.asText(), "expected 'blockquoted'"

def test_percent_table_style(): 
    """http://code.pediapress.com/wiki/ticket/39. thanks xyb."""
    
    def check(s):
        r = parse(s)
        t=r.find(parser.Table)[0]
        print t
        assert t.vlist['width'] == u'80%', "got wrong value %r" % (t.vlist['width'],)


    check('{| class="toccolours" width="80%" |}')
    check('{| class="toccolours" width=80% |}')

def test_parseParams():
    pp = parser.parseParams
    def check(s, expected):
        res= parser.parseParams(s)
        print repr(s), "-->", res, "expected:", expected

        assert res==expected, "bad result"

    check("width=80pt", dict(width="80pt"))
    check("width=80ex", dict(width="80ex"))

def test_ol_ul():
    """http://code.pediapress.com/wiki/ticket/33"""

    r=parse("#num\n*bul\n")
    lists = r.find(parser.ItemList)    
    assert len(lists)==2

    r=parse("*num\n#bul\n")
    lists = r.find(parser.ItemList)    
    assert len(lists)==2

def test_nested_lists():
    """http://code.pediapress.com/wiki/ticket/33"""
    r=parse("""
# lvl 1
#* lvl 2
#* lvl 2
# lvl 1
""")
    lists = r.find(parser.ItemList)
    assert len(lists)==2, "expected two lists"

    outer = lists[0]
    inner = lists[1]
    assert len(outer.children)==2, "outer list must have 2 children"
    assert len(inner.children)==2, "inner list must have 2 children"

def test_nested_list_listitem():
    r=parse("** wurst\n")
    outer = r.find(parser.ItemList)[0]
    assert isinstance(outer.children[0], parser.Item), "expected an Item inside ItemList"
    
    
def test_image_link_colon():
    """http://code.pediapress.com/wiki/ticket/28"""
    img = uparser.simpleparse("[[:Image:DNA orbit animated.gif|Large version]]").find(parser.ImageLink)[0]
    print img, img.colon
    assert img.colon, "expected colon attribute to be True"

    img = uparser.simpleparse("[[Image:DNA orbit animated.gif|Large version]]").find(parser.ImageLink)[0]
    print img, img.colon
    assert not img.colon, "expected colon attribute to be False"


def checktag(tagname):
    source = "<%s>foobar</%s>" % (tagname, tagname)
    r=parse(source)
    print "R:", r
    nodes=r.find(parser.TagNode)
    print "NODES:", nodes
    assert len(nodes)==1, "expected a TagNode"
    n = nodes[0]
    assert n.caption==tagname, "expected another node"
    
def test_strike_tag():
    checktag("strike")

def test_del_tag():
    checktag("del")

def test_ins_tag():
    checktag("ins")

def test_tt_tag():
    checktag("tt")

def test_code_tag():
    checktag("code")

def test_center_tag():
    checktag("center")

def test_headings_nonclosed():
    r=parse("= nohead\nbla")
    print "R:", r
    sections = r.find(parser.Section)
    assert sections==[], "expected no sections"

def test_headings_unbalanced_1():
    r=parse("==head=")  # section caption should '=head'
    print "R:", r
    section = r.find(parser.Section)[0]
    print "SECTION:", section
    print "ASTEXT:", section.asText()

    assert section.level==1, 'expected level 1 section'
    assert section.asText()=='=head'


def test_headings_unbalanced_2():
    r=parse("=head==")  # section caption should 'head='
    print "R:", r
    section = r.find(parser.Section)[0]
    print "SECTION:", section
    print "ASTEXT:", section.asText()

    assert section.level==1, 'expected level 1 section'
    assert section.asText()=='head='

def test_headings_tab_end():
    r=parse("=heading=\t")
    print "R:", r
    assert isinstance(r.children[0], parser.Section)
    
def test_table_extra_cells_and_rows():
    """http://code.pediapress.com/wiki/ticket/19"""
    s="""
<table>
  <tr>
    <td>1</td>
  </tr>
</table>"""
    r=parse(s)
    cells=r.find(parser.Cell)
    assert len(cells)==1, "expected exactly one cell"
    
    rows=r.find(parser.Row)
    assert len(rows)==1, "expected exactly one row"

def test_table_rowspan():
    """http://code.pediapress.com/wiki/ticket/19"""
    s="""
<table align="left">
  <tr align="right">
    <td rowspan=3 colspan=18>1</td>
  </tr>
</table>"""
    r=parse(s)
    cells=r.find(parser.Cell)
    assert len(cells)==1, "expected exactly one cell"
    cell = cells[0]
    print "VLIST:", cell.vlist
    assert cell.vlist == dict(rowspan=3, colspan=18), "bad vlist in cell"

    row = r.find(parser.Row)[0]
    print "ROW:", row
    assert row.vlist == dict(align="right"), "bad vlist in row"

    table=r.find(parser.Table)[0]
    print "TABLE.VLIST:", table.vlist
    assert table.vlist == dict(align="left"), "bad vlist in table"

def test_extra_cell_stray_tag():
    """http://code.pediapress.com/wiki/ticket/18"""
    cells = parse("""
{|
| bla bla </sub> dfg sdfg
|}""").find(parser.Cell)
    assert len(cells)==1, "expected exactly one cell"



def test_gallery_complex():
    gall="""<gallery caption="Sample gallery" widths="100px" heights="100px" perrow="6">
Image:Drenthe-Position.png|[[w:Drenthe|Drenthe]], the least crowded province
Image:Flevoland-Position.png
Image:Friesland-Position.png|[[w:Friesland|Friesland]] has many lakes
Image:Gelderland-Position.png
Image:Groningen-Position.png
Image:Limburg-Position.png
Image:Noord_Brabant-Position.png 
Image:Noord_Holland-Position.png
Image:Overijssel-Position.png
Image:Zuid_Holland-Position.png|[[w:South Holland|South Holland]], the most crowded province
lakes
Image:Zeeland-Position.png
</gallery>
"""
    res=parse(gall).find(parser.TagNode)[0]
    print "VLIST:", res.vlist
    print "RES:", res

    assert res.vlist=={'caption': 'Sample gallery', 'heights': '100px', 'perrow': 6, 'widths': '100px'}
    assert len(res.children)==12, 'expected 12 children'
    assert isinstance(res.children[10], parser.Text), "expected text for the 'lakes' line"

def test_colon_nobr():
    tagnodes = parse(";foo\n:bar\n").find(parser.TagNode)
    assert not tagnodes, "should have no br tagnodes"


def test_nonascii_in_tags():
    r = parse(u"<dfg\u0147>")
