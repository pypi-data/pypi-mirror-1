#! /usr/bin/env python
#! -*- coding:utf-8 -*-

import simplejson

## book = {'type':'collection',
##         'title':'',
##         'subtitle':'',
##         'items':[{'type':'chapter', 'title':'', 'items':[
##                                     {'type':'article',
##                                      'title':'',
##                                      'revision':'',
##                                      'authors':['',]},
##                                      'categories': ['']},
##                                      'text':'',
##                                     ]},
##                    ],
##         'source': {
##           'name': '',
##           'url': '',
##         },
##         'bookFormat':'', # A5,letter,...
##         'pageMargins':(), # 4 tuple with margins in mm (top,right,bottom,left)
##         'displayHeader': True,
##         'displayFooter':True,
##         'parseTree':'',
##         }


class MetaBook(object):

    def __init__(self, title='', subtitle='', items=[], bookFormat='', pageMargins = (0,0,0,0), displayHeader=True, displayFooter=True, parseTree=None, baseURL=''):
        for (_var, _value) in locals().items():
            if _var != 'self':
                setattr(self,_var, _value)      
        
    def addArticles(self, articleTitles, chapterTitle=None):
        articleList = []
        for title in articleTitles:
            article = {'type': 'article',
                       'title': title}
            articleList.append(article)
        if chapterTitle:
            chapter = {'type': 'chapter',
                       'title': chapterTitle,
                       'items': articleList}    
            self.items.append(chapter)
        else:
            self.items = articleList
    
    def dumpJson(self):
        jsonStr = vars(self)
        return simplejson.dumps(jsonStr)

    def loadJson(self,jsonBookStr):
        book = simplejson.loads(jsonBookStr)
        for (_var, _value) in book.items():
            setattr(self,_var, _value)

    def readJsonFile(self,jsonFile):
        jsonBookStr = open(jsonFile).read()
        self.loadJson(jsonBookStr)
    
    def getArticles(self):
        for item in self.getItems():
            if item['type'] == 'article':
                yield item['title'], item.get('revision', None)
    
    def getItems(self):
        items = []
        for item in self.items:
            if item['type'] == 'article':
                items.append(item)
            elif item['type'] == 'chapter':
                items.append(item)
                for article in item['items']:
                    items.append(article)
        return items

    def getFirstArticleTitle(self):
        for item in self.getItems():
            if item['type'] == 'article':
                return item['title']


if __name__ == '__main__':

    book = MetaBook(title='Der Asien Urlaub', subTitle='Wunderbar wirds!', author='Volker Haas')

    book.addArticles(['Philippinen','Pazifischer Ozean','Manila'], 'Die Philippinen')
    book.addArticles(['Mindoro','Luzon'],'Inseln')
    book.addArticles(['Philippinengraben','Seebeben','Tsunami'],'Natur & Geographie')

    
    #book.loadJson('{"subTitle": "", "pageMargins": [0, 0, 0, 0], "author": "", "displayHeader": true, "title": "Testbuch", "bookFormat": "", "displayFooter": true, "content": [{"articleList": [{"articleTitle": "Mainz", "authors": [], "revision": null}, {"articleTitle": "Rhein", "authors": [], "revision": null}, {"articleTitle": "Deutschland", "authors": [], "revision": null}], "chapterTitle": "Test Kapitel 1"}, {"articleList": [{"articleTitle": "Bier", "authors": [], "revision": null}, {"articleTitle": "Wurst", "authors": [], "revision": null}], "chapterTitle": "Zwotes Kapitel"}], "parseTree": null, "id": ""}')
    jsonStr = book.dumpJson()
    f=open('book.json','w')
    f.write(jsonStr)
    f.close()
    #print book.getArticleTitles()
