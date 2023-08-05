from cogplanet.model import *
from elementtree import ElementTree

def import_opml(opml):
    doc = ElementTree.parse(opml)
    feeds = []
    for outline in doc.findall('//outline'):
        feed = Feed()
        feed.htmlurl = outline.get('htmlUrl')
        feed.xmlurl = outline.get('xmlUrl')
        feed.name = outline.get('title')
        feeds.append(feed)
        print outline.get('xmlUrl')
    return(feeds)

