from pydataportability.xrds.parser import XRDSParser
from pkg_resources import resource_stream

def main():
        # egg style retrieval of the file "xrds.xml"
        fp = resource_stream(__name__, 'xrds.xml')
        p = XRDSParser(fp)
        fp.close()
        for s in p.services:
            print "Type:",s.type
            print "Prio:",s.priority
            print "LocalID:",s.localid        
            for uri in s.uris:
                print "  ",uri.uri
                
            print 


            print 
