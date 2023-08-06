# -*- coding: utf-8 -*-
###############################################################################
# $Copy$
###############################################################################
""" Utility for bibliography conversions


$Id: utility.py 64110 2008-05-02 07:03:38Z tom_gross $
"""
__docformat__ = 'reStructuredText'
__author__  = 'Tom Gross <itconsense@gmail.com>'

# python imports
from subprocess import Popen, PIPE
import logging

# zope2 imports
ZOPE2 = False
try:
    from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2Base
    import Acquisition
    ZOPE2 = True    
    UtilityBaseClass = Acquisition.Explicit
except ImportError:
    UtilityBaseClass = object

# zope3 imports
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implements
from zope.publisher.browser import TestRequest
from zope.traversing.browser.absoluteurl import absoluteURL

# plone imports
    
# third party imports

# own factory imports
from bibliograph.core.encodings import UNICODE_ENCODINGS
from bibliograph.core.encodings import _python_encodings
from bibliograph.core.interfaces import IBibliographyExport
from bibliograph.core.interfaces import IBibliographicReference
from bibliograph.core.utils import _convertToOutputEncoding
from bibliograph.core.utils import title_or_id
from bibliograph.core.utils import _encode
from bibliograph.rendering.interfaces import IBibTransformUtility

log = logging.getLogger('bibliograph.rendering')

###############################################################################

commands = {'bib2xml':'bib2xml',
            'copac2xml':'copac2xml',
            'end2xml':'end2xml',
            'isi2xml':'isi2xml',
            'med2xml':'med2xml',
            'ris2xml':'ris2xml',
            'xml2bib':'xml2bib',
            'xml2end':'xml2end',
            'xml2ris':'xml2ris',
            'copac2bib':'copac2xml | xml2bib ',
            'end2bib':'end2xml | xml2bib ',
            'isi2bib':'isi2xml | xml2bib ',
            'med2bib':'med2xml | xml2bib ',
            'ris2bib':'ris2xml | xml2bib ',
            'bib2end':'bib2xml | xml2end -o unicode',
            'bib2ris':'bib2xml | xml2ris -o unicode',
            'copac2end':'copac2xml | xml2end ',
            'isi2end':'isi2xml | xml2end ',
            'med2end':'med2xml | xml2end ',
            'ris2end':'ris2xml | xml2end ',
            'end2ris':'end2xml | xml2ris ',
            'copac2ris':'copac2xml | xml2ris ',
            'isi2ris':'isi2xml | xml2ris ',
            'med2ris':'med2xml | xml2ris ',
            }

def _getKey(source_format, target_format):
    return '2'.join([source_format, target_format])

###############################################################################

class ExternalTransformUtility(object):

    implements(IBibTransformUtility)

    def render(self, data, source_format, target_format, output_encoding=None):
        """ Transform data from 'source_format'
            to 'target_format'
    
            We have nothing, so we do nothing :)
            >>> ExternalTransformUtility().render('', 'bib', 'end')
            ''
    
            >>> data = '''
            ...   @Book{bookreference.2008-02-04.7570607450,
            ...     author = {Werner, kla{\"u}s},
            ...     title = {H{\"a}rry Motter},
            ...     year = {1980},
            ...     publisher = {Diogenes}
            ...   }'''
    
            This should work. We transform the `bib`-format into the `end`-
            format
            >>> print ExternalTransformUtility().render(data, 'bib', 'end')
            %0 Book
            %A Werner, kla"us title =. H"arry Motter
            %D 1980
            %I Diogenes
            %F bookreference.2008-02-04.7570607450
            <BLANKLINE>
            <BLANKLINE>
    
            This one is not allowed. No valid transformer exists for
            `foo` and `bar` (foo2bar)
            >>> ExternalTransformUtility().render(data, 'foo', 'bar')
            Traceback (most recent call last):
            ...
            ValueError: No transformation from 'foo' to 'bar' found.
    
        """
        key = _getKey(source_format, target_format)
        command = commands.get(key, None)
        if command is None:
            raise ValueError, "No transformation from '%s' to '%s' found." \
                  % (source_format, target_format)
    
        p = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE,
                  close_fds=True)
        (fi, fo, fe) = (p.stdin, p.stdout, p.stderr)
        fi.write(_encode(data))
        fi.close()
        result = fo.read()
        fo.close()
        error = fe.read()
        fe.close()
        if error:
            # command could be like 'ris2xml', or 'ris2xml | xml2bib'. It
            # seems unlikely, but we'll code for an arbitrary number of
            # pipes...
            command_list = command.split(' | ')
            for each in command_list:
                if each in error and not result:
                    log.error("'%s' not found. Make sure 'bibutils' is installed.",
                              command)
        if output_encoding is None:
            return result
        else:
            return _convertToOutputEncoding(result,
                                            output_encoding=output_encoding)

    transform = render
    
###############################################################################

class BibtexExport(UtilityBaseClass):
    
    implements(IBibTransformUtility)
    
    __name__ = u'BibTeX'
    source_format = None
    target_format = u'bib'
    description = u''
    available_encodings = _python_encodings
    default_encoding = u''

    available = True
    enabled = True
    
    def render(self, objects, output_encoding=None,
                     title_force_uppercase=False,
                     msdos_eol_style=False):
        """ Export a bunch of bibliographic entries in bibex format.
        """
        resolve_unicode = output_encoding not in UNICODE_ENCODINGS
    
        if not isinstance(objects, (list, tuple)):
            objects = [objects]
    
        request = getattr(objects[0], 'REQUEST', None)
        if request is None:
            request = TestRequest()
    
        if IBibliographyExport.providedBy(objects[0]):
            # tim2p: Begin some memory optimization for BTree-ish folder types.
            # There is an element of hack to this. While it relies on a public
            # method, that method is on a private ('_tree') attribute.
            # Well, it saves me 90MB of RAM for my c.700 ref database,
            # so I'm happy :).
            if ZOPE2:
                if isinstance(objects[0], BTreeFolder2Base):
                    with_btree_memory_efficiency = True
                    entries = objects[0]._tree.itervalues()
                else:
                    with_btree_memory_efficiency = False
                    entries = objects[0].contentValues()
            else:
                pass
                # XXX let this work for zope3
            rendered = []
            for entry in entries:
                if with_btree_memory_efficiency:
                    # _tree.itervalues() returns unwrapped objects,
                    # but renderEntry needs
                    # context-aware objects, so we wrap it.
                    # Check to see if the object has been changed (elsewhere in the
                    # current transaction/request.
                    changed = getattr(entry, '_p_changed', False)
                    deactivate = not changed
                    if ZOPE2:
                        entry = entry.__of__(objects[0])
                    else:
                        pass
                        # XXX let this work for zope3
                adapter = IBibliographicReference(entry, None)
                if adapter is None: continue
                view = getMultiAdapter((adapter, request),
                                       name=u'bibliography.bib')
                bibtex_string = view.render(
                    resolve_unicode=resolve_unicode,
                    title_force_uppercase=title_force_uppercase,
                    msdos_eol_style=msdos_eol_style,
                    )
                rendered.append(bibtex_string)
                if with_btree_memory_efficiency and deactivate:
                    # We now 'unload' the entry from the ZODB object cache to
                    # reclaim its memory.
                    # See http://wiki.zope.org/ZODB/UnloadingObjects for details.
                    # XXX In fact, there are probably no bad side-effects to
                    # making this call even if not with_btree_memory_effiency.
                    # However, I want my patch to be
                    # as non-intrusive as possible, so I don't do that now.
                    entry._p_deactivate()
            return _convertToOutputEncoding(''.join(rendered),
                                            output_encoding=output_encoding)
    
        # processing a single or a list of BibRef Items
        else:
            rendered = []
            for entry in objects:
                view = getMultiAdapter((entry, request),
                                       name=u'bibliography.bib')
                bibtex = view.render(
                    resolve_unicode=resolve_unicode,
                    title_force_uppercase=title_force_uppercase,
                    msdos_eol_style=msdos_eol_style)
                rendered.append(bibtex)
            if output_encoding is not None:
                return _convertToOutputEncoding(''.join(rendered),
                                            output_encoding=output_encoding)
            else:
                return ''.join(rendered)
        return ''
    
###############################################################################

class EndnoteExport(UtilityBaseClass):
    """ Export a bunch of bibliographic entries in endnote format.
    """
    
    implements(IBibTransformUtility)

    __name__ = u'EndNote'
    source_format = u'bib'
    target_format = u'end'
    description = u''
    
    available = True
    enabled = True

    available_encodings = _python_encodings
    default_encoding = u''
    
    def render(self, objects, output_encoding=None,
                     title_force_uppercase=False,
                     msdos_eol_style=False):
        """ do it 
        """
        source = BibtexExport().render(objects,
                              output_encoding='iso-8859-1',
                              title_force_uppercase=title_force_uppercase,
                              msdos_eol_style=msdos_eol_style)
        transform = getUtility(IBibTransformUtility, name=u"external")  
        return transform.render(source,
                                self.source_format,
                                self.target_format,
                                output_encoding)
             
###############################################################################

class RisExport(EndnoteExport):
    """ Export a bunch of bibliographic entries in ris format.
    """
    __name__ = u'RIS'    
    target_format = u'ris'
    description = u''
    
    available = True
    enabled = True

###############################################################################

class PdfExport(UtilityBaseClass):
    """ Export a bunch of bibliographic entries in pdf format.
    """

    implements(IBibTransformUtility)

    __name__ = u'PDF'
    source_format = u''
    target_format = u'pdf'
    description = u''
    
    available = True
    enabled = True

    available_encodings = []
    default_encoding = u''

    def render(self, objects, output_encoding=None,
                     title_force_uppercase=False,
                     msdos_eol_style=False):
        """ do it
        """
        if not isinstance(objects, (list, tuple)):
            objects = [objects]
    
        source = BibtexExport().render(objects,
                              output_encoding='iso-8859-1',
                              title_force_uppercase=True)  
        context = objects[0] 
        request = getattr(context, 'REQUEST', TestRequest())
        view = getMultiAdapter((context, request), name=u'bibliography.pdf')
        return view.processSource(source,
                                  title=title_or_id(context),
                                  url=absoluteURL(context, request))

###############################################################################

class XmlExport(EndnoteExport):
    """ Export a bunch of bibliographic entries in xml format.
    """
   
    __name__ = u'XML (MODS)'
    target_format = u'xml'
    description = u''
    
    available = True
    enabled = True

# EOF
