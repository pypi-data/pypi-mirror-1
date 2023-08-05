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
"""RML Directive Implementation

$Id: directive.py 73805 2007-03-28 03:02:22Z srichter $
"""
__docformat__ = "reStructuredText"
import logging
import zope.interface
import zope.schema

from z3c.rml import interfaces

logger = logging.getLogger("z3c.rml")


class RMLDirective(object):
    zope.interface.implements(interfaces.IRMLDirective)
    signature = None
    factories = {}

    def __init__(self, element, parent):
        self.element = element
        self.parent = parent

    def getAttributeValues(self, ignore=None, select=None, attrMapping=None,
                           includeMissing=False, valuesOnly=False):
        """See interfaces.IRMLDirective"""
        items = []
        for name, attr in zope.schema.getFieldsInOrder(self.signature):
            # Only add the attribute to the list, if it is supposed there
            if ((ignore is None or name not in ignore) and
                (select is None or name in select)):
                # Get the value.
                value = attr.bind(self).get()
                # If no value was found for a required field, raise a value
                # error
                if attr.required and value is attr.missing_value:
                    raise ValueError(
                        'No value for required attribute %s' %name)
                # Only add the entry if the value is not the missing value or
                # missing values are requested to be included.
                if value is not attr.missing_value or includeMissing:
                    items.append((name, value))

        # Sort the items based on the section
        if select is not None:
            select = list(select)
            items = sorted(items, key=lambda (n, v): select.index(n))

        # If the attribute name does not match the internal API
        # name, then convert the name to the internal one
        if attrMapping:
            items = [(attrMapping.get(name, name), value)
                     for name, value in items]

        # Sometimes we only want the values without the names
        if valuesOnly:
            return [value for name, value in items]

        return items

    def processSubDirectives(self, select=None, ignore=None):
        # Go through all children of the directive and try to process them.
        for element in self.element.getchildren():
            if select is not None and element.tag not in select:
                continue
            if ignore is not None and element.tag in ignore:
                continue
            # If the element is a directive, process it
            if element.tag in self.factories:
                directive = self.factories[element.tag](element, self)
                directive.process()
            else:
                # Record any tags/elements that could not be processed.
                logger.warn("Directive %r could not be processed and was "
                            "ignored." %element.tag)

    def process(self):
        self.processSubDirectives()
