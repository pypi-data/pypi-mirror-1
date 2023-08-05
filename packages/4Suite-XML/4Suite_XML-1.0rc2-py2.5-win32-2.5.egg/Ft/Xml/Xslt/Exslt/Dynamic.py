"""
EXSLT 2.0 - Dyanmic (http://www.exslt.org/dyn/index.html)
WWW: http://4suite.org/XSLT        e-mail: support@4suite.org

Copyright (c) 2001 Fourthought Inc, USA.   All Rights Reserved.
See  http://4suite.org/COPYRIGHT  for license and copyright information
"""

from Ft.Xml.XPath import parser
from Ft.Xml.XPath import Conversions
from Ft.Xml.Xslt import XsltRuntimeException, Error
from Ft.Xml.Xslt.CopyOfElement import CopyNode

EXSL_DYNAMIC_NS = "http://exslt.org/dynamic"

##def Closure(context, nodeset, string):
##    """
##    The dyn:closure function creates a node set resulting from transitive
##    closure of evaluating the expression passed as the second argument on
##    each of the nodes passed as the first argument, then on the node set
##    resulting from that and so on until no more nodes are found.
##
##    Implements version 1.
##    """
##    if type(nodeset) != type([]):
##        raise XsltRuntimeException(Error.WRONG_ARGUMENT_TYPE,
##                                   context.currentInstruction)
##    string = Conversions.StringValue(string)
##    return


def Evaluate(context, string):
    """
    The dyn:evaluate function evaluates a string as an XPath expression and
    returns the resulting value, which might be a boolean, number, string,
    node set, result tree fragment or external object. The sole argument is
    the string to be evaluated.

    Implements version 1.
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


def Map(context, nodeset, string):
    """
    The dyn:map function evaluates the expression passed as the second
    argument for each of the nodes passed as the first argument, and returns
    a node set of those values.

    Implements version 1.
    """
    if type(nodeset) != type([]):
        raise XsltRuntimeException(Error.WRONG_ARGUMENT_TYPE,
                                   context.currentInstruction)
    string = Conversions.StringValue(string)
    p = parser.new()
    ctx = context.clone()
    try:
        result = []
        for n in nodeset:
            ctx.node = n
            result.append(p.parse(string).evaluate(ctx))
    except:
        import traceback
        traceback.print_exc()
        result = []
    return result


##def Max(context, nodeset, string):
##    """
##    The dyn:max function calculates the maximum value for the nodes passed as
##    the first argument, where the value of each node is calculated dynamically
##    using an XPath expression passed as a string as the second argument.
##
##    Implements version 1.
##    """
##    if type(nodeset) != type([]):
##        raise XsltRuntimeException(Error.WRONG_ARGUMENT_TYPE,
##                                   context.currentInstruction)
##    string = Conversions.StringValue(string)
##    return


##def Min(context, nodeset, string):
##    """
##    The dyn:min function calculates the minimum value for the nodes passed as
##    the first argument, where the value of each node is calculated dynamically
##    using an XPath expression passed as a string as the second argument.
##
##    Implements version 1.
##    """
##    if type(nodeset) != type([]):
##        raise XsltRuntimeException(Error.WRONG_ARGUMENT_TYPE,
##                                   context.currentInstruction)
##    string = Conversions.StringValue(string)
##    return


##def Sum(context, nodeset, string):
##    """
##    The dyn:sum function calculates the sum for the nodes passed as the first
##    argument, where the value of each node is calculated dynamically using an
##    XPath expression passed as a string as the second argument.
##
##    Implements version 1.
##    """
##    if type(nodeset) != type([]):
##        raise XsltRuntimeException(Error.WRONG_ARGUMENT_TYPE,
##                                   context.currentInstruction)
##    string = Conversions.StringValue(string)
##    return

ExtNamespaces = {
    EXSL_DYNAMIC_NS : 'dyn',
    }

ExtFunctions = {
    #(EXSL_DYNAMIC_NS, 'closure') : Closure,
    (EXSL_DYNAMIC_NS, 'evaluate') : Evaluate,
    (EXSL_DYNAMIC_NS, 'map') : Map,
    #(EXSL_DYNAMIC_NS, 'max') : Max,
    #(EXSL_DYNAMIC_NS, 'min') : Min,
    #(EXSL_DYNAMIC_NS, 'sum') : Sum,
}

ExtElements = {}
