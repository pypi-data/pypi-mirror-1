import ots
import sys

try:
    filename = sys.argv[1]
except:
    filename="example.txt"

o = ots.OTS()
o.parse(filename, 20)
print "parsed"
print "Title:", o.title
print "Lines:", o.lineCount
print "Summary:"
print o


from codecs import open
d =open(filename, 'r').read()
d = d.decode('utf-8').encode('utf-8')
o = ots.OTS()
o.parseUnicode(d)
print "Title:", o.title
print "Lines:", o.lineCount
print "Summary:"
print o.asHTML()


print o.hilite()
print

print o.topics()
print o.topics_stemmed()
