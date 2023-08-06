##########################################################################
# SmartPrintNG - high-quality export of Plone content to
# PDF, RTF, ODT, WML and DOCX
#
# (C) 2007, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

"""
Factory for converters
"""

from zope.interface import implements, implementedBy
from zope.component.interfaces import IFactory

from zopyx.convert import Converter

class Factory:
    """ zopyx.convert.Converter factory """
    
    implements(IFactory)

    def __init__(self, klass):
        self._klass = klass

    def __call__(self, *args, **kw):
        return self._klass(*args, **kw)

    def getInterfaces(self):
        return implementedBy(self._klass)

Factory = Factory(Converter)
