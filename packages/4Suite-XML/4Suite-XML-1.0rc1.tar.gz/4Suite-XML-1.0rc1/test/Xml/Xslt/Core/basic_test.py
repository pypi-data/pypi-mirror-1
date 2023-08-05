from Xml.Xslt import test_harness
from Ft.Lib import Uri
import os

sheet_2 = """<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  version="1.0"
  >
  <xsl:output method="html"/>

  <xsl:template match="/">
    <HTML>
    <HEAD><TITLE>Address Book</TITLE>
    </HEAD>
    <BODY>
    <H1><xsl:text>Tabulate just the Names</xsl:text></H1>
    <TABLE><xsl:apply-templates/></TABLE>
    </BODY>
    </HTML>
  </xsl:template>

  <xsl:template match="ENTRY">
        <TR>
        <xsl:apply-templates select='NAME|PHONENUM'/>
        </TR>
  </xsl:template>

  <xsl:template match="NAME">
    <TD ALIGN="CENTER">
      <B><xsl:apply-templates/></B>
    </TD>
  </xsl:template>

</xsl:stylesheet>
"""

sheet_3 = """<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  version="1.0"
  >

  <xsl:strip-space elements="*"/>

  <xsl:template match="/">
    <HTML>
    <HEAD><TITLE>Address Book</TITLE>
    </HEAD>
    <BODY>
    <H1><xsl:text>Tabulate just the Names</xsl:text></H1>
    <TABLE><xsl:apply-templates/></TABLE>
    </BODY>
    </HTML>
  </xsl:template>

  <xsl:template match="ADDRBOOK">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="ENTRY">
    <TR>
      <xsl:apply-templates/>
    </TR>
  </xsl:template>

  <xsl:template match="NAME">
    <TD ALIGN="CENTER">
      <B><xsl:apply-templates/></B>
    </TD>
  </xsl:template>

  <xsl:template match="*"/>

</xsl:stylesheet>
"""

sheet_4 = """<?xml version="1.0"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:A="http://spam.org"
  version="1.0"
  >

  <xsl:output method="html"/>

  <xsl:template match="/">
    <HTML>
    <HEAD><TITLE>Address Book</TITLE>
    </HEAD>
    <BODY>
    <H1><xsl:text>Tabulate just the Names</xsl:text></H1>
    <TABLE><xsl:apply-templates/></TABLE>
    </BODY>
    </HTML>
  </xsl:template>

  <xsl:template match="A:ENTRY">
        <TR>
        <xsl:apply-templates select='A:NAME|A:PHONENUM'/>
        </TR>
  </xsl:template>

  <xsl:template match="A:NAME">
    <TD ALIGN="CENTER">
      <B><xsl:apply-templates/></B>
    </TD>
  </xsl:template>

</xsl:stylesheet>
"""


source_4 = """<?xml version = "1.0"?>
<?xml-stylesheet type="text/xml" href="Xml/Xslt/Core/addr_book1.xsl"?>
<!DOCTYPE ADDRBOOK [
  <!ELEMENT ADDRBOOK (ENTRY*)>
  <!ATTLIST ADDRBOOK
    xmlns CDATA #FIXED 'http://spam.org'
  >
  <!ELEMENT ENTRY (NAME, ADDRESS, PHONENUM*, EMAIL)>
  <!ATTLIST ENTRY
    ID ID #REQUIRED
  >
  <!ELEMENT NAME (#PCDATA)>
  <!ELEMENT ADDRESS (#PCDATA)>
  <!ELEMENT PHONENUM (#PCDATA)>
  <!ATTLIST PHONENUM
    DESC CDATA #REQUIRED
  >
  <!ELEMENT EMAIL (#PCDATA)>
]>
<ADDRBOOK>
    <ENTRY ID="pa">
        <NAME>Pieter Aaron</NAME>
        <ADDRESS>404 Error Way</ADDRESS>
        <PHONENUM DESC="Work">404-555-1234</PHONENUM>
        <PHONENUM DESC="Fax">404-555-4321</PHONENUM>
        <PHONENUM DESC="Pager">404-555-5555</PHONENUM>
        <EMAIL>pieter.aaron@inter.net</EMAIL>
    </ENTRY>
    <ENTRY ID="en">
        <NAME>Emeka Ndubuisi</NAME>
        <ADDRESS>42 Spam Blvd</ADDRESS>
        <PHONENUM DESC="Work">767-555-7676</PHONENUM>
        <PHONENUM DESC="Fax">767-555-7642</PHONENUM>
        <PHONENUM DESC="Pager">800-SKY-PAGEx767676</PHONENUM>
        <EMAIL>endubuisi@spamtron.com</EMAIL>
    </ENTRY>
    <ENTRY ID="vz">
        <NAME>Vasia Zhugenev</NAME>
        <ADDRESS>2000 Disaster Plaza</ADDRESS>
        <PHONENUM DESC="Work">000-987-6543</PHONENUM>
        <PHONENUM DESC="Cell">000-000-0000</PHONENUM>
        <EMAIL>vxz@magog.ru</EMAIL>
    </ENTRY>
</ADDRBOOK>"""



expected_1 = """<html>
  <head>
    <meta http-equiv='Content-Type' content='text/html; charset=iso-8859-1'>
    <title>Address Book</title>
  </head>
  <body>
    <h1>Tabulate Just Names and Phone Numbers</h1>
    <table>
      <tr>
        <td align='center'><b>Pieter Aaron</b></td>
        <td>(Work) 404-555-1234<br>(Fax) 404-555-4321<br>(Pager) 404-555-5555</td>
      </tr>
      <tr>
        <td align='center'><b>Emeka Ndubuisi</b></td>
        <td>(Work) 767-555-7676<br>(Fax) 767-555-7642<br>(Pager) 800-SKY-PAGEx767676</td>
      </tr>
      <tr>
        <td align='center'><b>Vasia Zhugenev</b></td>
        <td>(Work) 000-987-6543<br>(Cell) 000-000-0000</td>
      </tr>
    </table>
  </body>
</html>"""

expected_2 = """<HTML>
  <HEAD>
    <meta http-equiv='Content-Type' content='text/html; charset=iso-8859-1'>
    <TITLE>Address Book</TITLE>
  </HEAD>
  <BODY>
    <H1>Tabulate just the Names</H1>
    <TABLE>
      <TR>
        <TD ALIGN='CENTER'><B>Pieter Aaron</B></TD>404-555-1234404-555-4321404-555-5555</TR>
      <TR>
        <TD ALIGN='CENTER'><B>Emeka Ndubuisi</B></TD>767-555-7676767-555-7642800-SKY-PAGEx767676</TR>
      <TR>
        <TD ALIGN='CENTER'><B>Vasia Zhugenev</B></TD>000-987-6543000-000-0000</TR>
    </TABLE>
  </BODY>
</HTML>"""

expected_3 = """<HTML>
  <HEAD>
    <meta http-equiv='Content-Type' content='text/html; charset=iso-8859-1'>
    <TITLE>Address Book</TITLE>
  </HEAD>
  <BODY>
    <H1>Tabulate just the Names</H1>
    <TABLE>
      <TR>
        <TD ALIGN='CENTER'><B>Pieter Aaron</B></TD>
      </TR>
      <TR>
        <TD ALIGN='CENTER'><B>Emeka Ndubuisi</B></TD>
      </TR>
      <TR>
        <TD ALIGN='CENTER'><B>Vasia Zhugenev</B></TD>
      </TR>
    </TABLE>
  </BODY>
</HTML>"""

expected_4 = """<HTML xmlns:A='http://spam.org'>
  <HEAD>
    <meta http-equiv='Content-Type' content='text/html; charset=iso-8859-1'>
    <TITLE>Address Book</TITLE>
  </HEAD>
  <BODY>
    <H1>Tabulate just the Names</H1>
    <TABLE>
      <TR>
        <TD ALIGN='CENTER'><B>Pieter Aaron</B></TD>404-555-1234404-555-4321404-555-5555</TR>
      <TR>
        <TD ALIGN='CENTER'><B>Emeka Ndubuisi</B></TD>767-555-7676767-555-7642800-SKY-PAGEx767676</TR>
      <TR>
        <TD ALIGN='CENTER'><B>Vasia Zhugenev</B></TD>000-987-6543000-000-0000</TR>
    </TABLE>
  </BODY>
</HTML>"""


def Test(tester):

    source = test_harness.FileInfo(uri='Xml/Xslt/Core/addr_book1.xml')
    sheet = test_harness.FileInfo(uri='Xml/Xslt/Core/addr_book1.xsl')
    test_harness.XsltTest(tester, source, [sheet], expected_1,
                          title='test 1')


    source = test_harness.FileInfo(uri='Xml/Xslt/Core/addr_book1.xml')
    sheet = test_harness.FileInfo(string=sheet_2)
    test_harness.XsltTest(tester, source, [sheet], expected_2,
                          title='test 2')


    source = test_harness.FileInfo(uri='Xml/Xslt/Core/addr_book1.xml')
    sheet = test_harness.FileInfo(string=sheet_3)
    test_harness.XsltTest(tester, source, [sheet], expected_3,
                          title='test 3')


    source = test_harness.FileInfo(string=source_4, validate=1)
    sheet = test_harness.FileInfo(string=sheet_4)
    test_harness.XsltTest(tester, source, [sheet], expected_4,
                          title='test 4')


    # Appending explicit stylesheet when xml-stylesheet PI already
    # specifies one results in both stylesheets being appended. If
    # it's the same stylesheet, it's an error.
    #
    #source = test_harness.FileInfo(uri='Xml/Xslt/Core/addr_book1.xml')
    #sheet = test_harness.FileInfo(uri='Xml/Xslt/Core/addr_book1.xsl')
    #    test_harness.XsltTest(tester, source, [sheet], expected_1, ignorePis=0,
    #                          title='test 5')

    return
