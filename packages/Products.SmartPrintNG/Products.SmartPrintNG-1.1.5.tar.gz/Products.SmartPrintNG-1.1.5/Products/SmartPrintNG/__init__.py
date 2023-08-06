##########################################################################
# SmartPrintNG - high-quality export of Plone content to
# PDF, RTF, ODT, WML and DOCX
#
# (C) 2007, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################


from Products.CMFCore.DirectoryView import registerDirectory

registerDirectory('skins', globals())

def initialize(context):

    import converters
