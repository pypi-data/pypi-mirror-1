##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Page Template Support

$Id: pagetemplate.py 73904 2007-03-29 11:34:12Z srichter $
"""
__docformat__ = "reStructuredText"
import zope
from z3c.rml import rml2pdf

try:
    import zope.pagetemplate.pagetemplatefile
except ImportError:
    # zope.pagetemplate package has not been installed
    import types
    zope.pagetemplate = types.ModuleType('barcode')
    zope.pagetemplate.pagetemplatefile = types.ModuleType('barcode')
    zope.pagetemplate.pagetemplatefile.PageTemplateFile = object


class RMLPageTemplateFile(zope.pagetemplate.pagetemplatefile.PageTemplateFile):

    def pt_getContext(self, args=(), options=None, **ignore):
        rval = {'template': self,
                'args': args,
                'nothing': None,
                'context': options
                }
        rval.update(self.pt_getEngine().getBaseNames())
        return rval

    def __call__(self, *args, **kwargs):
        rml = super(RMLPageTemplateFile, self).__call__(*args, **kwargs)

        # RML is a unicode string, but oftentimes documents declare their
        # encoding using <?xml ...>. Unfortuantely, I cannot tell lxml to
        # ignore that directive. Thus we remove it.
        if rml.startswith('<?xml'):
            rml = rml.split('\n', 1)[-1]

        return rml2pdf.parseString(rml).getvalue()
