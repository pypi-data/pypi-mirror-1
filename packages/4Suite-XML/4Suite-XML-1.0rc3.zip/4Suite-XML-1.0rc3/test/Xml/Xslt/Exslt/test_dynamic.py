########################################################################
# $Header: /var/local/cvsroot/4Suite/test/Xml/Xslt/Exslt/Attic/test_dynamic.py,v 1.1.2.1 2006/08/27 22:15:46 uogbuji Exp $
"""Tests for EXSLT Dynamic"""

from Xml.Xslt import test_harness

TESTS = []

SOURCE = """<doc><otu id='1'/><abuo id='2'/><ato id='3'/><ano id='4'/></doc>"""

# dyn:evaluate()
def test_evaluate(tester):
    TRANSFORM = """<?xml version='1.0' encoding='UTF-8'?>
<xsl:transform
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:dyn="http://exslt.org/dynamic"
  exclude-result-prefixes="dyn"
  version="1.0"
>

  <xsl:template match="doc">
    <result>
      <xsl:for-each select="*">
        <num>
          <xsl:value-of select="dyn:evaluate(concat('name(/doc/*[', position(), '])'))"/>
        </num>
      </xsl:for-each>
    </result>
  </xsl:template>

</xsl:transform>
"""

    EXPECTED = '<?xml version="1.0" encoding="UTF-8"?>\n<result><num>otu</num><num>abuo</num><num>ato</num><num>ano</num></result>'

    source = test_harness.FileInfo(string=SOURCE)
    transform = test_harness.FileInfo(string=TRANSFORM)
    test_harness.XsltTest(tester, source, [transform], EXPECTED,
                          title='dyn:evaluate()')
    return

TESTS.append(test_evaluate)
    

# dyn:map()
def test_map(tester):
    TRANSFORM = """<?xml version='1.0' encoding='UTF-8'?>
<xsl:transform
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:dyn="http://exslt.org/dynamic"
  exclude-result-prefixes="dyn"
  version="1.0"
>

  <xsl:template match="doc">
    <result>
      <xsl:for-each select="dyn:map(*, '@id')">
        <num>
          <xsl:value-of select="."/>
        </num>
      </xsl:for-each>
    </result>
  </xsl:template>

</xsl:transform>
"""

    EXPECTED = '<?xml version="1.0" encoding="UTF-8"?>\n<result><num>1</num><num>2</num><num>3</num><num>4</num></result>'

    source = test_harness.FileInfo(string=SOURCE)
    transform = test_harness.FileInfo(string=TRANSFORM)
    test_harness.XsltTest(tester, source, [transform], EXPECTED,
                          title='dyn:map()')
    return

TESTS.append(test_map)
    

# dyn:closure()
#FIXME: Not a very good test: exercises closure logic, but not dynamic expression evaluation
def test_closure(tester):
    TRANSFORM = """<?xml version='1.0' encoding='UTF-8'?>
<xsl:transform
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:dyn="http://exslt.org/dynamic"
  exclude-result-prefixes="dyn"
  version="1.0"
>

  <xsl:template match="doc">
    <result>
      <xsl:for-each select="dyn:closure(*, '*[@x]')">
        <node>
          <xsl:value-of select="@x"/>
        </node>
      </xsl:for-each>
    </result>
  </xsl:template>

</xsl:transform>
"""

    SOURCE2 = """<doc><a x='1'><e x='2'/></a><b x='3'><f/></b><c><g x='4'/></c><d x='5'><h x='6'/></d></doc>"""

    EXPECTED = '<?xml version="1.0" encoding="UTF-8"?>\n<result><node>2</node><node>4</node><node>6</node></result>'

    source = test_harness.FileInfo(string=SOURCE2)
    transform = test_harness.FileInfo(string=TRANSFORM)
    test_harness.XsltTest(tester, source, [transform], EXPECTED,
                          title='dyn:closure()')
    return

TESTS.append(test_closure)
    

def Test(tester):
    tester.startGroup('EXSLT Dynamic module')
    for test in TESTS:
        test(tester)
    tester.groupDone()
    return

