import os, sys
#from Ft.Xml.Xslt import XsltElement, AttributeInfo
from Xml.Xslt import test_harness

XMLDECL = '<?xml version="1.0" encoding="UTF-8"?>\n'

SOURCE_1 = '<doc>&#x2713;</doc>' #Char data is the check mark character

SHEET_1 = """<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:ext="urn:x-4suite:x"
>

  <xsl:template match="/">
    <xsl:value-of select='ext:ord(.)'/>
  </xsl:template>

</xsl:stylesheet>
"""

EXPECTED_1 = XMLDECL + str(int('2713', 16))

def Test(tester):
    tester.startGroup("Test ord extension function example")

    extmod = '.'.join(__name__.split('.')[:-1] + ['ord'])
    source = test_harness.FileInfo(string=SOURCE_1)
    sty = test_harness.FileInfo(string=SHEET_1)
    test_harness.XsltTest(tester, source, [sty], EXPECTED_1,
                          extensionModules=[extmod])
    tester.groupDone()


