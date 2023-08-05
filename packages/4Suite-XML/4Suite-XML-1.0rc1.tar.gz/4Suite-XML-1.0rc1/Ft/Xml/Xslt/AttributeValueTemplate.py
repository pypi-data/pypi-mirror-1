########################################################################
# $Header: /var/local/cvsroot/4Suite/Ft/Xml/Xslt/AttributeValueTemplate.py,v 1.10 2006/01/11 22:12:29 jkloth Exp $
"""
Implementation of XSLT attribute value templates

Copyright 2006 Fourthought, Inc. (USA).
Detailed license and copyright information: http://4suite.org/COPYRIGHT
Project home, documentation, distributions: http://4suite.org/
"""

from Ft.Xml.Xslt import XsltException, Error
from Ft.Xml.XPath import Conversions

import AvtParserc
_AvtParser = AvtParserc.AvtParser()
del AvtParserc

class AttributeValueTemplate:

    def __init__(self, source, validator=None, element=None):
        self.source = source
        self.validator = validator
        self.element = element

        try:
            # parts is a list of unicode and/or parsed XPath
            parts = _AvtParser.parse(source)
        except SyntaxError, exc:
            raise XsltException(Error.AVT_SYNTAX)

        self._resultFormat = u""
        self._parsedParts = parsed_parts = []
        for part in parts:
            if isinstance(part, unicode):
                self._resultFormat += part
            else:
                self._resultFormat += u"%s"
                parsed_parts.append(part)
        return

    def isConstant(self):
        return not self._parsedParts

    def evaluate(self, context):
        if not self.element and hasattr(context, 'currentInstruction'):
            self.element = context.currentInstruction

        convert = Conversions.StringValue
        result = self._resultFormat % tuple([ convert(x.evaluate(context))
                                              for x in self._parsedParts ])
        if self.validator:
            return self.validator.reprocess(self.element, result)
        else:
            return result

    def __nonzero__(self):
        return self.source is not None
