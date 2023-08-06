##########################################################################
# SmartPrintNG - high-quality export of Plone content to
# PDF, RTF, ODT, WML and DOCX
#
# (C) 2007, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

""" HTML manipulation methods """

import re
import random
from cStringIO import StringIO
from urlparse import urlparse
import urllib2
from logging import getLogger

from PIL import Image
from BeautifulSoup import BeautifulSoup, NavigableString, Tag

from Products.CMFCore.utils import getToolByName 

LOG = getLogger('SmartPrintNG')

def removeLinks(html):
    """ replace all links with a <span> tag and the anchor text """

    soup = BeautifulSoup(html)
    refs = soup.findAll('a')

    for x in refs:
        tag = Tag(soup,'span')
        tag.insert(0,x.renderContents().strip())
        soup.a.replaceWith(tag)
    return  str(soup)

def removeReviewHistory(html):

    soup = BeautifulSoup(html)
    for x in soup.findAll(id='review-history'):
        x.extract()
    return  str(soup)


def removeImages(html):
    """ Remove all images """

    soup = BeautifulSoup(html)
    images = soup.findAll('img')
    [img.extract() for img in images]
    return  str(soup)


def checkHref(href):
    """ Return False for mailto|javascript or internal
        anchors or views.
    """

    if 'mailto:' in href or \
       'javascript:' in href or \
       href.startswith('#') or \
       href.startswith('@@'):
           return False
    return True
       

def getLinksInHtml(html):
    """ return all links inside a HTML fragment """

    soup = BeautifulSoup(html)
    hrefs = []
    for anchor in soup.findAll('a'):

        # we need to capture internal anchors
        try:
            href = anchor['href']
        except:
            continue 

        if href in hrefs or not checkHref(href):
           continue

        hrefs.append(str(href))
    return hrefs


def _pcdataFromNode(s, lst=[]):
    """ recursive pcdata collector """

    if s.string is not None:
        lst.append(s.string)
    else:
        for n in s.contents:
            _pcdataFromNode(n, lst)
    return ' '.join(lst)


def enumerateLinksInHtml(html, links):

    soup = BeautifulSoup(html)

    count = 1
    links = []
    for anchor in soup.findAll('a'):

        # capture internal anchors
        try:
            href = anchor['href']
        except KeyError:
            continue

        if not checkHref(href):
            continue

        anchor['class'] = 'enumerated-link'
        s = _pcdataFromNode(anchor) + ' [%d]' % count
        anchor.contents = [NavigableString(s)]
        links.append(anchor['href'])
        count += 1
        
    return str(soup)
    

def addLinkList(html):

    links = getLinksInHtml(html)
    html = enumerateLinksInHtml(html, links)

    if links:                      
        pat = '<li>[%d] %s</li>'
        link_string = '\n'.join([pat % (i+1, link) for i, link in enumerate(links)])
        linkLst = '\n<div class="enumerated-links"><ol>%s</ol</div>' % link_string
        html = html + linkLst

    return html


def handleImages(context, html, tempdir):

    mt = getToolByName(context, 'portal_membership')
    http_host = context.REQUEST.HTTP_HOST

    def fixImages(img):

        src = img['src'].encode('ascii')

        # we convert always to PNG in order to support *all*
        # external converters because they support different image types
        new_img = '%s/%s.png' % (tempdir, random.random())

        tp = urlparse(src)
        img_data = ''

        same_host = http_host == tp[1]
        if tp[0] in ('http', 'https', 'ftp') and not same_host:
            # appears like a remote image, download it
            url = src
            try:
                img_data = urllib2.urlopen(url).read()
            except Exception, e:
                LOG.error('Could not get image from %s (%s)' % (url, e))
        else:
            # likely a local image, try to traverse to get hold
            # of the image data directly
            img_path = src
            if img_path.startswith('./'): # FCKeditor 
                img_path = img_path[2:]

            img_obj = None
            for path in (img_path, tp[2]):        
                img_obj = context.unrestrictedTraverse(path, None)
                if img_obj:
                    if mt.checkPermission('View', img_obj):
                        try:
                            img_data = str(img_obj.data)
                            break
                        except AttributeError:
                            try:
                                img_data = str(img_obj._data) # FSImage
                            except AttributeError:
                                break

        if img_data:        
            pil_img= Image.open(StringIO(img_data))
            pil_img.save(new_img, 'PNG')
            img['src'] = new_img
        else:
            img.extract()

    soup = BeautifulSoup(html)
    for img in soup.findAll('img'):
        fixImages(img)
    html = str(soup)
    return html


def breakIntoPages(html, seperator='(h1|h2)'):

    breaker = re.compile('<%s' % seperator, re.I|re.M|re.S)

    div_start = '<div class="chapter sp-page">'
    div_start2 = '<div class="chapter">'
    div_end = '</div>'

    positions = []
    for mo in breaker.finditer(html):
        positions.append(mo.start())
    positions.append(len(html))

    parts = []
    len_positions = len(positions) - 1
    for i in range(len_positions):
        start = positions[i]
        end = positions[i+1]

        if i == len_positions - 1:
            parts.append(div_start2 + html[start: end].strip() + div_end)
        else:
            parts.append(div_start + html[start: end].strip() + div_end)

    return '\n'.join(parts)



available_manipulations = (
    {'label' : 'removeImages', 'method' : removeImages, 'description': 'Remove images', 'state' : False},
    {'label' : 'removeLinks', 'method' : removeLinks, 'description': 'Remove links', 'state' : False},
    {'label' : 'addLinkList', 'method' : addLinkList, 'description': 'Add link list', 'state' : False},
    {'label' : 'breakIntoPages', 'method' : breakIntoPages, 'description': 'Break into pages', 'state' : False},
    {'label' : 'removeReviewHistory', 'method' : removeReviewHistory, 'description': 'Remove review history', 'state' : True},
)
