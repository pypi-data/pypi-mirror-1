##########################################################################
# SmartPrintNG - high-quality export of Plone content to
# PDF, RTF, ODT, WML and DOCX
#
# (C) 2007, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

"""
Multipurpose HTML extractor for Plone content
"""

from BeautifulSoup import BeautifulSoup


def standard_html_extractor(obj):
    """ Extract HTML from an object by rendering it. """

    html = obj.view()
    soup = BeautifulSoup(html)
    body = str(soup.findAll('div', {'class' : 'documentContent'})[0])
    return body
