from zope.component import provideUtility, getUtilitiesFor
from xfn import XFNParser, IXFNParser

# register the hCard parser
provideUtility(XFNParser,IXFNParser,name="xfn")

