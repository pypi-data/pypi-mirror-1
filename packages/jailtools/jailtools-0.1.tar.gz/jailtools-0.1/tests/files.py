import sys

print "File"
f = open("/file", "wb")
f.write(sys.stdin.read())
f.close()
print "Written"
