##########################################################################
# SmartPrintNG - high-quality export of Plone content to
# PDF, RTF, ODT, WML and DOCX
#
# (C) 2007, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

"""'
ZCML directives for SmartPrintNG
"""

import os
import logging

from zope.interface import Interface
from zope.schema import TextLine 
import zope.configuration.fields


registry = {}                   
LOG = logging.getLogger()


class ISmartPrintNGResourceDirectory(Interface):
    """ Used for specifying SmartPrintNG resources """

    directory = TextLine(
        title=u"Directory name",
        description=u'Directory path containing templates and styles for a given interface',
        default=u"",
        required=True)

    interfaces = zope.configuration.fields.Tokens(
        title=u"For interfaces",
        description=u'Register resource directory for these interfaces',
        required=True,
        value_type=zope.configuration.fields.GlobalInterface())


def resourceDirectory(_context, directory, interfaces):

    # path of ZCML file
    zcml_filename = _context.info.file

    for iface in interfaces:

        if registry.has_key(iface):
            raise ValueError('%s has already a configured resources directory' % iface)

        # directory name relative to the ZCML directory
        dirname = os.path.join(os.path.dirname(zcml_filename), directory)
        if not os.path.exists(dirname):
            raise IOError('SmartPrintNG resource directory %s does not exist' % dirname)

        d = {'templates' : [], 'stylesheets' : [], 'fo_stylesheets' : []}

        map = {'.pt' : 'templates', 
               '.css' : 'stylesheets', 
               '.fo_css' : 'fo_stylesheets'}

        # scan for templates and stylesheets
        for fname in os.listdir(dirname):

            filename = os.path.join(dirname, fname)
            if not os.path.isfile(filename):
                continue
            basename, ext = os.path.splitext(fname)
            key = map.get(ext)
            if key is not None:
                d[key].append((basename, filename))
            else:
                LOG.warn('Unsupported file type found: %s' % filename)
                continue

        # register resources for interface only if there is something
        # to  be registered
        if d['templates'] or d['stylesheets']:                
            registry[iface] = d

