##########################################################################
# SmartPrintNG - high-quality export of Plone content to
# PDF, RTF, ODT, WML and DOCX
#
# (C) 2007, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import os            
import random
import tempfile

from zope.interface import implements, implementedBy
from zope.component.interfaces import IFactory
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile

from Products.SmartPrintNG.interfaces import IConverter
from Products.SmartPrintNG.zcml import registry

from manipulation import available_manipulations, handleImages

# map mainpulation label -> method
manipulations_d = {}
for d in available_manipulations:
    manipulations_d[d['label']] = d['method']


class Converter(object):

    implements(IConverter)

    def __init__(self):
        self.id = str(random.random())
        self.tempdir = os.path.join(tempfile.gettempdir(), 'smartprinting', self.id)
        if not os.path.exists(self.tempdir):
            os.makedirs(self.tempdir)


    def convert(self, context, html, options, **kw):

        """ 'options' is a record-style datastructure with basically
            to attributes: 'workchain' representing a list of 
            HTML manipulation methods represented by their names and
            'template' represents to name of a template to render
            the full HTML.
        """

        # pre-process HTML fragment by running through a pipeline 
        # of converters/manipulation methods
        workchain = getattr(options, 'workchain', ())
        for d in available_manipulations:
            if d['label'] in workchain:
                html = d['method'](html)

        # now pass the modified HTML fragment to the template
        # in order to render a proper HTML file

        d = {'title' : 'Standardconverter',
             'body' : unicode(html, 'utf-8'), 
             'stylesheet' : getattr(options, 'stylesheet', 'default.css'),
            }

        # Search for the corresponding template in out registry
        for iface, d2 in registry.items():

            # first check if the interface is provided by the current
            # context object
            if not iface.providedBy(context):
                continue

            for name, template_filename in d2['templates']:
                if name == options.template:
                    template = ViewPageTemplateFile(template_filename)
                    # we need to set the debug flag to make the code
                    # work on Plone 2.5 aka Zope 2.9
                    context.request.debug = False
                    html = template(context, **d)
                    break

        # Last, fix all image links and export all related images 
        # into the filesystem
        html = handleImages(context, html, self.tempdir)

        return html


class Factory:
    
    implements(IFactory)

    def __init__(self, klass):
        self._klass = klass

    def __call__(self):
        return self._klass()

    def getInterfaces(self):
        return implementedBy(self._klass)

Factory = Factory(Converter)
