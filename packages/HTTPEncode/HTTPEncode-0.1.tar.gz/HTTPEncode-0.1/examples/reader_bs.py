#!/usr/bin/env python
import optparse
import urllib
import string
import textwrap
from httpencode import *
http = HTTP()

parser = optparse.OptionParser()
parser.add_option('-q', '--query',
                  help="The query",
                  dest="query")

url = 'http://www.chicagoreader.com/cgi-bin/ListingScripts/MuSearch.cgi'

def show_results(query):
    form = dict(
        Real='WorkReal',
        StartMuSearchBut='Start Search',
        MusicString=query)
    data = http.POST(url, output='BeautifulSoup',
                     body=form)
    for item in data.findAll('h1'):
        title = item.find('b')
        if title:
            title = tcontents(title).title()
            print '*', title
        span = item.find('span')
        if span:
            span.extract()
        for img in item.findAll('img'):
            img.extract()
        for color in item.findAll('font'):
            color.replaceWith(tcontents(color))
        for link in item.findAll('a'):
            if not link.get('href'):
                continue
            href = link['href'].replace('\n', '').replace('\r', '')
            link.replaceWith('%s <%s>' % (tcontents(link), href))
        desc = tcontents(item).strip()
        for line in textwrap.wrap(desc):
            print '  %s' % line

def tcontents(tag):
    return ''.join(map(unicode, tag.contents))

if __name__ == '__main__':
    options, args = parser.parse_args()
    if not options.query:
        print 'You must give --query'
        parser.exit()
    show_results(options.query)

