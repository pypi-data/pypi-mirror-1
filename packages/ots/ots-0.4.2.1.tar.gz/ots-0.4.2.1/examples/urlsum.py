#!/usr/bin/python -O
import ots
import sys, os
import urllib
import stripogram
from optparse import OptionParser
import webbrowser
import tempfile

try:
    import chardet
except ImportError:
    class chardet:
        @staticmethod
        def detect(data):
            return {'encoding' : sys.getdefaultencoding()}
        

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

    parser.add_option('-p', '--percentage',
                      dest="percentage",
                      default=20,
                      type="int",
                      help="percentage of doc to retain"
                      )
                      


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
    o.percentage = options.percentage
    o.parseUnicode(data)
    
    if options.html:
        fd, fn = tempfile.mkstemp(".html")
        os.write(fd, o.asHTML())
        os.close(fd)
        webbrowser.open("file://%s" %fn)
    else:
        print "Title:", o.title
        print "Lines:", o.lineCount
        
        print o.topics()
        print o.topics_stemmed()
        
