##########################################################################
# SmartPrintNG - high-quality export of Plone content to
# PDF, RTF, ODT, WML and DOCX
#
# (C) 2007, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

"""
Adapters for specific Plone content types (basicially used
for demonstration purposes.
"""

from zope.interface import implements
from zope.component import adapts

from Products.SmartPrintNG.interfaces import IHTMLExtractor 
from Products.ATContentTypes.interface.folder import IATFolder


class ATFolderMultiplePagesAdapter(object):
    """ ATFolder adapter that generates the concatenation of all documents within
        the current folder.
    """

    adapts(IATFolder)
    implements(IHTMLExtractor)

    def __init__(self, context):
        self.context = context

    def getHTML(self, context):
        """ Return all Documents inside the current folder (not from any subtrees)
            as HTML snippet.
        """

        div_start = '<div class="chapter sp-page">'
        div_start2 = '<div class="chapter">'
        div_end = '</div>'

        lst = []
        brains =  self.context.portal_catalog(portal_type='Document',
                                              path={'query' : '/'.join(self.context.getPhysicalPath()), 'level' : 0},
                                              sort_on='getObjPositionInParent',
                                              )
        num_brains = len(brains)
        for i, brain in enumerate(brains):
            doc = brain.getObject()
            lst.append( (i != num_brains - 1 and div_start or div_start2) + 
                        doc.getText() +
                        div_end)

        return '\n'.join(lst)            
