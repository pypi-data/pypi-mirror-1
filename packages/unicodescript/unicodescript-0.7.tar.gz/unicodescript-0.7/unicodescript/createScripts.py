"""
    Utility for ./createScripts.sh
"""
import sys
a = -1

ahex = lambda x: hex(x)[2:].upper().rjust(5,"0")

arange = lambda x,y: ahex(x) + ".." + ahex(y)

for line in sys.stdin.readlines():
    start = int(line[:5],16)
    if not start == a + 1:
        print arange(a + 1, start - 1) +" Zzzz"
    a = int(line[7:13],16)
    print line, 
    
print arange(a + 1, int("FFFFF",16)) + " Zzzz"
