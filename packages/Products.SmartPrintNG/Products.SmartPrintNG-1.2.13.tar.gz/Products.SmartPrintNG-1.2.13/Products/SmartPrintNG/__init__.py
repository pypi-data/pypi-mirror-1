##########################################################################
# SmartPrintNG - high-quality export of Plone content to
# PDF, RTF, ODT, WML and DOCX
#
# (C) 2007, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

# Import "MessageFactory" to create messages in the smartprintng domain
from zope.i18nmessageid import MessageFactory
SPNGMessageFactory = MessageFactory('smartprintng')

from Products.CMFCore.DirectoryView import registerDirectory

registerDirectory('skins', globals())

def initialize(context):

    import converters
