#!/usr/bin/python -O
import ots
import sys
import urllib
import stripogram
from optparse import OptionParser
import chardet



if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option('-l', "--lang",
                      dest="language",
                      default="en",
                      help="Specify the two letter language code")

    parser.add_option('-H', "--html",
                      dest="html",
                      default=False,
                      action="store_true",
                      help="Specify the two letter language code")

    (options, args) = parser.parse_args()

    url = args[0]

    #get the file
    fp = urllib.urlopen(url)
    data = fp.read()

    # strip the html
    
    data = stripogram.html2text(data)
    enc = chardet.detect(data)['encoding']
    data = data.decode(enc).encode('utf-8')

    o = ots.OTS(options.language)
    o.parseUnicode(data)
    
    if options.html:
        print o.asHTML()
    else:
        print "Title:", o.title
        print "Lines:", o.lineCount
        
        print o.topics()
        print o.topics_stemmed()
        
