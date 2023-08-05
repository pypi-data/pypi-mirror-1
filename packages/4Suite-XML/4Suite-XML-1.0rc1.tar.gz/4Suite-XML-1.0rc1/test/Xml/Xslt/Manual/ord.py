#ord.py
from Ft.Xml.XPath import Conversions

def Ord(context, s):
    '''
    Available in XPath as ord() as defined by ExtFunctions mapping below
    Takes an object, which is coerced to string
    Returns the Unicode code point number for the first character in that string
    Or returns -1 if it's an empty string
    '''
    s = Conversions.StringValue(s)  #Coerce the passed object to string
    if s:
        return ord(s[0])
    else:
        return -1

ExtFunctions = {
    (u'urn:x-4suite:x', u'ord'): Ord,
}

