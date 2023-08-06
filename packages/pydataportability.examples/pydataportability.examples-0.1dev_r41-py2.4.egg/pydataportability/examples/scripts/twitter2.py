from zope.component import getUtility

from pkg_resources import resource_string

import pydataportability.microformats.hcard
import pydataportability.microformats.xfn

from pydataportability.microformats.base.htmlparsers.etree import ElementTreeHTMLParser
from pydataportability.microformats.base.interfaces import IHTMLParser

def main():
    # egg style retrieval of the file "m2.html"
    data = resource_string(__name__, 'm2.html')

    parser = getUtility(IHTMLParser,name="beautifulsoup")()
    mf = parser.fromString(data)
    mf.parse()

    for name,result in mf.microformats.items():
        print "**",name,"**"
        for r in result:
            print r
    


