##########################################################################
# SmartPrintNG - high-quality export of Plone content to
# PDF, RTF, ODT, WML and DOCX
#
# (C) 2007, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import os
import tempfile
import logging
import threading

from Globals import InitializeClass
from Products.Five import BrowserView
from ZPublisher.Iterators import filestream_iterator

from zope.interface import providedBy
from zope.component import createObject, getAdapters, getAdapter
from zope.component.interfaces import ComponentLookupError

try:
    from zope.contenttype import guess_content_type
except ImportError:
    from OFS.content_types import guess_content_type

from Products.SmartPrintNG.interfaces import IHTMLExtractor
from standard_extractor import standard_html_extractor
from zcml import registry

C_LOCK = threading.Lock()
conversions_in_progres = 0

LOG = logging.getLogger()

class SmartPrintView(BrowserView):

    def convert(self, 
                html=None, 
                options=(),
                format='pdf', 
                content_extractor='',
                print_options={},
                converter_name='zopyx.smartprintng.converters.default',
                xslfo_converter_name='zopyx.smartprintng.converters.xslfo',
                redirect=False,
                **kw):
        """ Convert a html snippet to format.
            'html' - a HTML snippet. If not available IHTMLExtractor is being used
                     for extracting HTML fro the current object.

            'options' - a converter specific datastructure passed directly to the converter

            'print_options' - dict of options passed as cmdline parameters down to css2xslfo

            'format' - rtf|pdf|pdf|odt|docx|wml

            'converter_name' - name of a registered converter utility
        """

        if content_extractor:
            # ATT: error handling
            try:
                extractor = getAdapter(self.context, IHTMLExtractor, name=content_extractor)
                html = extractor.getHTML(self.context)
            except ComponentLookupError:
                html = standard_html_extractor(self.context)

        # create up converter utility
        converter = createObject(converter_name)

        # 'html' should utf-8 encoded (from encodeURIComponent)
        html = converter.convert(self.context, html, options, **kw)

        # convert it back to 'utf-8', if necessary
        if isinstance(html, unicode):
            html = html.encode('utf-8')

        # Store HTML as a temporary file 
        tmpf = tempfile.mktemp()
        open(tmpf, 'wb').write(html)

        # and start the XSL-FO converter
        xslfoConverter = createObject(xslfo_converter_name, tmpf, encoding='utf-8')

        ok = False
        try:
            output_filename = xslfoConverter.convert(format, **dict(print_options))
            ok = True
        except:
            LOG.error('Error during conversion', exc_info=True)
            ok = False

        os.unlink(tmpf)

        if redirect:
            if ok:
                return self.request.RESPONSE.redirect(self.context.absolute_url() + 
                                                     '/smartPrintDeliver?filename=%s' % output_filename)
            raise RuntimeError('Error converting file')

        else:
            if ok:
                return output_filename
            raise RuntimeError('Error converting file')


    def deliver(self, filename):
        """ stream generated file back to client """

        def normalize(s):
            s = s.replace(' ', '_')
            return s

        filename = os.path.abspath(filename)
        if not filename.startswith(tempfile.gettempdir()):
            raise RuntimeError('Can not download %s' % filename)

        type, enc = guess_content_type(filename)
        base, ext = os.path.splitext(os.path.basename(filename))
        id = normalize(self.context.getId())

        R = self.context.request.RESPONSE
        R.setHeader('content-type', type)
        R.setHeader('content-length', os.stat(filename)[6])
        R.setHeader('content-disposition', 'attachment; filename=%s%s' % (id, ext))
        filename = os.path.abspath(filename)
        return filestream_iterator(filename, 'rb')


    def availableFormats(self):
        """ Return a list of all support formats """
        from zopyx.convert import availableFormats
        return availableFormats()


    def availableTemplates(self):
        """ Return a list of tuples (template_name, description) """
        lst = list()

        # all registered interfaces for SmartPrintNG resources
        all_ifaces = registry.keys()

        # get all interfaces from the current object
        for iface in providedBy(self.context).flattened():

            # check if interface is registered for SmartPrintNG
            if iface in all_ifaces:
                d = registry[iface]

                # add list of available templates to result list
                for id, template in registry[iface]['templates']:
                    lst.append((id, id))

        return lst

    def availableStylesheets(self):
        """ Return a list of tuples (stylesheet_name, description) """
        lst = list()

        # all registered interfaces for SmartPrintNG resources
        all_ifaces = registry.keys()

        # get all interfaces from the current object
        for iface in providedBy(self.context).flattened():

            # check if interface is registered for SmartPrintNG
            if iface in all_ifaces:
                d = registry[iface]

                # add list of available templates to result list
                for id, template in registry[iface]['stylesheets']:
                    lst.append((id, id))

        return lst

    def _getStylesheet(self, name, registry_key):
        """ Return a FO related stylesheet by name """

        # all registered interfaces for SmartPrintNG resources
        all_ifaces = registry.keys()

        # get all interfaces from the current object
        for iface in providedBy(self.context).flattened():

            # check if interface is registered for SmartPrintNG
            if iface in all_ifaces:
                d = registry[iface]

                # add list of available templates to result list
                for id, sheet in registry[iface][registry_key]:
                    if id == name:
                        return open(sheet).read()

        raise ValueError('No stylesheet %s found' % name)


    def getFOStylesheet(self, name):
        """ Return a FO related stylesheet """
        return self._getStylesheet(name, 'fo_stylesheets')


    def getStylesheet(self, name):
        """ Return a standard stylesheet """
        return self._getStylesheet(name, 'stylesheets')


    def availableOptions(self):
        """ Return manipulations dict """
        from converter.manipulation import available_manipulations
        return available_manipulations


    def availableContentExtractors(self):
        """ return all names of registered IHTMLExtractor adapters for 
            the current context object.
        """
        return [name for name, adapter in getAdapters((self.context,), IHTMLExtractor)]

InitializeClass(SmartPrintView)
