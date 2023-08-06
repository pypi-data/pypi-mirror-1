##########################################################################
# SmartPrintNG - high-quality export of Plone content to
# PDF, RTF, ODT, WML and DOCX
#
# (C) 2007, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

from zope.interface import Interface

class IConverter(Interface):

    def convert(context, html, **kw):
        """ A converter takes a snippet of HTML code and returns
            a valid XHTML page containing the snippet of HTML 
            in *some* way.
        """


class IHTMLExtractor(Interface):
    """ Extract a HTML snippet from the current object """

    def getHTML(context=None):
        """ Returns a HTML snippet to be converted for the current
            object. The method *must* not returned a full HTML page.
            An optional context object will be passed if the interface
            is implemented by an utility.
        """


