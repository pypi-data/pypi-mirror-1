#!/usr/bin/env python
import optparse
import urllib
import string
from httpencode import *
from lxml import etree
http = HTTP()

parser = optparse.OptionParser()
parser.add_option('-q', '--query',
                  help="The query",
                  dest="query")

query_url = string.Template('http://www.google.com/search?q=$query&num=100')

def show_results(query):
    url = query_url.substitute(query=urllib.quote(query))
    data = http.GET(url, output='lxml')
    items = data.xpath("//a[@class='l']")
    print 'Found %s items' % len(items)
    if not items:
        print etree.tostring(data)
    for item in items:
        print item.attrib['href']

if __name__ == '__main__':
    options, args = parser.parse_args()
    if not options.query:
        print 'You must give --query'
        parser.exit()
    show_results(options.query)

