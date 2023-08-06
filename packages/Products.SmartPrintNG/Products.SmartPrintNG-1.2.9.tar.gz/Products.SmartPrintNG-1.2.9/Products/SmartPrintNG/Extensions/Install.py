##########################################################################
# SmartPrintNG - high-quality export of Plone content to
# PDF, RTF, ODT, WML and DOCX
#
# (C) 2007, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################


from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import getFSVersionTuple

def install(self, reinstall=False):

    
    mtool = getToolByName(self, 'portal_migration')
    plone_version = mtool.getFileSystemVersion()
    if plone_version.startswith('3.0'):
        version = '3.0'
    elif plone_version.startswith('3.1'):
        version = '3.1'
    elif plone_version.startswith('3.2'):
        version = '3.2'
    else:
        raise RuntimeError('Unsupported Plone version %s' % plone_version)

    tool=getToolByName(self, "portal_setup")

    if version == '3.0':
        tool.runAllImportStepsFromProfile(
                "profile-Products.SmartPrintNG:smartprintng",
                purge_old=False)
    else:
        tool.runAllImportStepsFromProfile(
                "profile-Products.SmartPrintNG:default",
                purge_old=False)
