# akin to weeklyreddit
# but for HN

import httplib2, lxml
from lxml.html import parse
from StringIO import StringIO

print 'Using', lxml.__file__
print 'Using', httplib2.__file__


_h = httplib2.Http('httplib2-cache')
def open_url(url):
    """Open an URL and return a file-like object

    The request is cached using httplib2
    """
    resp, content = _h.request(url)
    return StringIO(content)

def zigzag(seq):
    """Return two sequences with alternating elements from `seq`"""
    x, y = [], []
    p, q = x, y
    for e in seq:
        p.append(e)
        p, q = q, p
    return x, y

def parse_int(s, default):
    try:
        return int(s)
    except ValueError:
        return default

def parse_mainpage(hnurl):
    doc = parse(open_url(hnurl)).getroot()
    links = doc.cssselect('td.title a')
    scores = doc.cssselect('td.subtext span')
    clinks = zigzag(doc.cssselect('td.subtext a'))[1]

    for l,s,cl in zip(links, scores, clinks):
        link = hnurl + cl.get('href')
        points = parse_int(s.text_content().split()[0], 1)
        comments = parse_int(cl.text_content().split()[0], 0)
        print u'[{0:3}] {1:50} ({2})\n      {3}'.format(
            points, l.text_content(), comments, link)

def parse_commentspage(url):
    parse_mainpage(url)

def main():
    hnurl = 'http://news.ycombinator.com/'
    parse_mainpage(hnurl)
    # parse_commentspage('http://news.ycombinator.com/item?id=829622')

if __name__ == '__main__':
    main()
