#!/usr/bin/python

from lxml import etree
import urllib
import repository

base = 'http://www.openclipart.org/cchost/media/api/search'

def get(url):
    return urllib.urlopen(url).read()

#TODO: add a function to test net access at program startup so we can disable stuff if not

class OCAL(object):

    def __init__(self, repo):
        self.repo = repo

    @staticmethod
    def testAccess():
        try:
            self.queryRSS('dog')
            return True
        except:
            return False

    @staticmethod
    def queryRSS(query):
        q = urllib.urlencode({'query':query})
        qUrl = base + '?' + q
        rss = urllib.urlopen(qUrl).read()
        doc = etree.fromstring(rss)
        items = doc.xpath('/rss/channel/item')
        output = []
        for item in items:
            try:
                d = {}
                d['url'] = item.xpath('enclosure/@url')[0]
                if not d['url'].endswith('.svg'):
                    continue
                d['title'] = item.xpath('title/text()')[0]
                output.append(d)
            except:
                pass
        return output

    def search(self, query):
        results = self.queryRSS(query)
        output = []
        for item in results:
            try:
                xml = urllib.urlopen(item['url']).read()
                output.append(self.repo.addImage(xml=xml))
            except: 
                pass
        return output
