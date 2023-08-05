"""
EXSLT 2.0 - Dyanmic (http://www.exslt.org/dyn/index.html)
WWW: http://4suite.org/XSLT        e-mail: support@4suite.org

Copyright (c) 2001 Fourthought Inc, USA.   All Rights Reserved.
See  http://4suite.org/COPYRIGHT  for license and copyright information
"""

from Ft.Lib import Set
from Ft.Xml.XPath import parser
from Ft.Xml.XPath import Conversions, XPathTypes
from Ft.Xml.Xslt import XsltRuntimeException, Error
from Ft.Xml.Xslt.CopyOfElement import CopyNode

EXSL_DYNAMIC_NS = "http://exslt.org/dynamic"


def Evaluate(context, string):
    """
    The dyn:evaluate function evaluates a string as an XPath expression and
    returns the resulting value, which might be a boolean, number, string,
    node set, result tree fragment or external object. The sole argument is
    the string to be evaluated.

    http://www.exslt.org/dyn/functions/evaluate/index.html
    """
    string = Conversions.StringValue(string)
    p = parser.new()
    try:
        result = p.parse(string).evaluate(context)
    except:
        import traceback
        traceback.print_exc()
        result = []
    return result


def MapImpl(context, nodeset, expr):
    ctx = context.clone()
    try:
        result = []
        size = len(nodeset)
        for index, n in enumerate(nodeset):
            ctx.node = n
            ctx.size = size
            ctx.pos = index + 1
            partial = expr.evaluate(ctx)
            if not isinstance(partial, XPathTypes.NodesetType):
                #FIXME: technically should make a list of text nodes here
                partial = [partial]
            result = Set.Union(result, partial)
    except:
        import traceback
        traceback.print_exc()
        result = []
    
    return result


def Map(context, nodeset, string):
    """
    The dyn:map function evaluates the expression passed as the second
    argument for each of the nodes passed as the first argument, and returns
    a node set of those values.

    http://www.exslt.org/dyn/functions/map/index.html
    """
    if type(nodeset) != type([]):
        raise XsltRuntimeException(Error.WRONG_ARGUMENT_TYPE,
                                   context.currentInstruction)
    string = Conversions.StringValue(string)
    expr = parser.new().parse(string)
    return MapImpl(context, nodeset, expr)


def ClosureImpl(context, nodeset, expr, accumulator):
    result = MapImpl(context, nodeset, expr)
    if result:
        accumulator.extend(result)
        ClosureImpl(context, result, expr, accumulator)
    return accumulator


def Closure(context, nodeset, string):
    """
    The dyn:closure function creates a node set resulting from transitive
    closure of evaluating the expression passed as the second argument on
    each of the nodes passed as the first argument, then on the node set
    resulting from that and so on until no more nodes are found.

    http://www.exslt.org/dyn/functions/closure/index.html
    """
    if type(nodeset) != type([]):
        raise XsltRuntimeException(Error.WRONG_ARGUMENT_TYPE,
                                   context.currentInstruction)
    string = Conversions.StringValue(string)
    expr = parser.new().parse(string)
    return ClosureImpl(context, nodeset, expr, [])



def Max(context, nodeset, string):
    """
    The dyn:max function calculates the maximum value for the nodes passed as
    the first argument, where the value of each node is calculated dynamically
    using an XPath expression passed as a string as the second argument.

    http://www.exslt.org/dyn/functions/max/index.html
    """
    if type(nodeset) != type([]):
        raise XsltRuntimeException(Error.WRONG_ARGUMENT_TYPE,
                                   context.currentInstruction)
    string = Conversions.StringValue(string)
    expr = parser.new().parse(string)
    return max([ Conversions.NumberValue(n)
                 for n in MapImpl(context, nodeset, expr) ])



def Min(context, nodeset, string):
    """
    The dyn:min function calculates the minimum value for the nodes passed as
    the first argument, where the value of each node is calculated dynamically
    using an XPath expression passed as a string as the second argument.
    
    http://www.exslt.org/dyn/functions/min/index.html
    """
    if type(nodeset) != type([]):
        raise XsltRuntimeException(Error.WRONG_ARGUMENT_TYPE,
                                   context.currentInstruction)
    string = Conversions.StringValue(string)
    expr = parser.new().parse(string)
    return max([ Conversions.NumberValue(n)
                 for n in MapImpl(context, nodeset, expr) ])


def Sum(context, nodeset, string):
    """
    The dyn:sum function calculates the sum for the nodes passed as the first
    argument, where the value of each node is calculated dynamically using an
    XPath expression passed as a string as the second argument.
    
    http://www.exslt.org/dyn/functions/sum/index.html
    """
    if type(nodeset) != type([]):
        raise XsltRuntimeException(Error.WRONG_ARGUMENT_TYPE,
                                   context.currentInstruction)
    string = Conversions.StringValue(string)
    expr = parser.new().parse(string)
    return sum([ Conversions.NumberValue(n)
                 for n in MapImpl(context, nodeset, expr) ])


ExtNamespaces = {
    EXSL_DYNAMIC_NS : 'dyn',
    }

ExtFunctions = {
    (EXSL_DYNAMIC_NS, 'closure') : Closure,
    (EXSL_DYNAMIC_NS, 'evaluate') : Evaluate,
    (EXSL_DYNAMIC_NS, 'map') : Map,
    (EXSL_DYNAMIC_NS, 'max') : Max,
    (EXSL_DYNAMIC_NS, 'min') : Min,
    (EXSL_DYNAMIC_NS, 'sum') : Sum,
}

ExtElements = {}
