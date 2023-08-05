from Ft.Lib import boolean, number
from Ft.Xml.Domlette import NonvalidatingReader
from Ft.Xml.XPath import ParsedExpr

class DummyBooleanExpr:
    def __init__(self,val):
        self.val = val and boolean.true or boolean.false

    def evaluate(self,context):
        return self.val

    def __repr__(self):
        return str(self.val)

class DummyNumberExpr:
    def __init__(self,val):
        self.val = val

    def evaluate(self,context):
        return self.val

    def __repr__(self):
        return str(self.val)

class DummyNodeSetExpr:
    def __init__(self, val=None):
        self.val = val

    def evaluate(self,context):
        return self.val

    def select(self,context):
        return self.val

    def __repr__(self):
        return '<%d-item nodeset>' % len(self.val)

class DummyStringExpr:
    def __init__(self, val=None):
        self.val = (val is None) and u'DummyString' or val

    def evaluate(self,context):
        return self.val

    def __repr__(self):
        return repr(self.val)


boolT = DummyBooleanExpr(1)
boolF = DummyBooleanExpr(0)

num0 = DummyNumberExpr(0)
num0p5 = DummyNumberExpr(0.5)
numN0p5 = DummyNumberExpr(-0.5)
num1 = DummyNumberExpr(1)
num1p5 = DummyNumberExpr(1.5)
num2 = DummyNumberExpr(2)
num2p6 = DummyNumberExpr(2.6)
num3 = DummyNumberExpr(3)
numN4 = DummyNumberExpr(-4)
num4p5 = DummyNumberExpr(4.5)
numN4p5 = DummyNumberExpr(-4.5)
numN42 = DummyNumberExpr(-42)
numNan = DummyNumberExpr(number.nan)
numInf = DummyNumberExpr(number.inf)
numNInf = DummyNumberExpr(-number.inf)

strEmpty = DummyStringExpr(u'')
str12345 = DummyStringExpr(u'12345')
strPi = DummyStringExpr(u'3.14')
strText = DummyStringExpr(u'Hi')
strPiText = DummyStringExpr(u'3.14Hi')
strSpace = DummyStringExpr(u'Ht    \t There\t   Mike')
strHelloWorld = DummyStringExpr(u'hello world')
STR_EGG1 = DummyStringExpr(u'egg1')
STR_EGG2 = DummyStringExpr(u'egg2')

DOC = "<spam><egg1>egg1</egg1><egg2>egg2</egg2></spam>"
doc = NonvalidatingReader.parseString(DOC, 'http://foo/test/spam.xml')
node1 = doc.documentElement.firstChild
node2 = node1.nextSibling

EMPTY_NODE_SET = DummyNodeSetExpr([])
ONE_NODE_SET = DummyNodeSetExpr([node1])
TWO_NODE_SET = DummyNodeSetExpr([node1, node2])

