from zope.component import provideUtility, getUtilitiesFor
from parser import HCardParser, IHCardParser

# register the hCard parser
provideUtility(HCardParser,IHCardParser,name="hcard")

