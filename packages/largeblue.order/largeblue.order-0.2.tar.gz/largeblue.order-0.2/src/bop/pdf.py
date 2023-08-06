#!/usr/local/env/python
#############################################################################
# Name:         pdf.py
# Purpose:      bop PDF creation methods
# Maintainer:   Torsten Kurbad <t.kurbad@iwm-kmrc.de>
# Copyright:    (c) 2008 iwm-kmrc.de KMRC - Knowledge Media Research Center
# Licence:      GPL
#############################################################################
__docformat__ = 'restructuredtext'

from cStringIO import StringIO

HAS_PISA = False
try:
    from ho import pisa
    import reportlab
    HAS_PISA = True
except ImportError:
    pass


class PDFError(Exception):
    """ Specialized exception for PDF creation errors. """


def html2pdf(htmlString, debug=0, errout=None, tempdir=None, format=None, link_callback=False, default_css=None, xhtml=False):
    """ Convert a string representation of HTML to
        a string representation of PDF.
    """
    if not HAS_PISA:
        return

    output = StringIO()
    pdf = pisa.pisaDocument(StringIO(htmlString),
                            output,
                            debug=debug,
                            errout=errout,
                            tempdir=tempdir,
                            format=format,
                            link_callback=link_callback,
                            default_css=default_css,
                            xhtml=xhtml)

    if not pdf.err:
        result = output.getvalue()
        output.close()
        return result

    raise PDFError(pdf.err)
