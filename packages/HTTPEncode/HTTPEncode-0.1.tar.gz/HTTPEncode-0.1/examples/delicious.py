#!/usr/bin/env python
import optparse
import string
import cgi
import sys
from httpencode import *
http = HTTP()

parser = optparse.OptionParser()
parser.add_option('-u', '--username',
                  help="Delicious username",
                  dest="username")
parser.add_option('-o', '--output',
                  help="Output format (text or default html)",
                  default='text',
                  dest='output')

delicious_url = string.Template(
    'http://del.icio.us/feeds/json/$username?raw')

item_html_template = string.Template(
    '  <li><a href="$link">$title</a>$tag_text$desc\n  </li>')
item_text_template = string.Template(
    '* $title <$link>$tag_text$desc\n')

def html_quote(v):
    return cgi.escape(unicode(v), 1)

def br_quote(v):
    return v.replace('\n', '<br>\n')

def show_feed(username, output, writer):
    url = delicious_url.substitute(username=username)
    data = http.GET(url, output='python')
    if output == 'html':
        writer('<ul>\n')
    for item in data:
        link = item['u']
        tags = item.get('t', [])
        title = item.get('d', link)
        desc = item.get('n', '')
        if tags:
            tag_text = '\n  tags: %s' % ', '.join(tags)
        else:
            tag_text = ''
        if desc:
            desc = '\n  ' + desc
        if output == 'html':
            writer(item_html_template.substitute(
                link=html_quote(link),
                title=html_quote(title),
                tag_text=br_quote(html_quote(tag_text)),
                desc=br_quote(html_quote(desc))))
        else:
            writer(item_text_template.substitute(
                link=link,
                title=title,
                tag_text=tag_text,
                desc=desc))
    if output == 'html':
        writer('</ul>\n')

def html_writer(text):
    if isinstance(text, unicode):
        text = text.encode('ascii', 'xmlcharrefreplace')
    sys.stdout.write(text)

def text_writer(text):
    if isinstance(text, unicode):
        text = text.encode('utf8')
    sys.stdout.write(text)
    
if __name__ == '__main__':
    options, args = parser.parse_args()
    if not options.username:
        print 'You must give --username'
        parser.exit()
    if options.output not in ('text', 'html'):
        print '--output must be one of "text" or "html"'
        parser.exit()
    if options.output == 'html':
        writer = html_writer
    else:
        writer = text_writer
    show_feed(options.username, options.output,
              writer)
    
