# demo.py
import time, urlparse
from Ft.Xml.XPath import Conversions

def GetCurrentTime(context):
    '''available in XPath as get-current-time()'''
    return time.asctime(time.localtime())

def HashContextName(context, maxkey):
    '''
    available in XPath as hash-context-name(maxkey),
    where maxkey is an object converted to number
    '''
    # It is a good idea to use the appropriate core function to coerce
    # arguments to the expected type
    maxkey = Conversions.NumberValue(maxkey)
    key = reduce(lambda a, b: a + b, context.node.nodeName)
    return key % maxkey

ExtFunctions = {
    ('urn:x-4suite:x', 'get-current-time'): GetCurrentTime,
    ('urn:x-4suite:x', 'hash-context-name'): HashContextName
}

