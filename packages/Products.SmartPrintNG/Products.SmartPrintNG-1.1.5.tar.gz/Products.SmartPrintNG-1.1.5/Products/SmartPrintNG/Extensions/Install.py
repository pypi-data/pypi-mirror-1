##########################################################################
# SmartPrintNG - high-quality export of Plone content to
# PDF, RTF, ODT, WML and DOCX
#
# (C) 2007, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################


from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import getFSVersionTuple

def install(self, reinstall=False):
    tool=getToolByName(self, "portal_setup")

    if getFSVersionTuple()[0]>=3:
        tool.runAllImportStepsFromProfile(
                "profile-Products.SmartPrintNG:smartprintng",
                purge_old=False)
    else:
        plone_base_profileid = "profile-CMFPlone:plone"
        tool.setImportContext(plone_base_profileid)
        tool.setImportContext("profile-Products.SmartPrintNG:plone25")
        tool.runAllImportSteps(purge_old=False)
        tool.setImportContext(plone_base_profileid)


