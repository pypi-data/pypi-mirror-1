import os
import unicodedata
import bisect

scriptfile = os.path.dirname (os.path.abspath (__file__))+"/scripts.txt"

indexes = []
scripts = []
def script(char):
    """
        Gets the Unicode Script property of any character. Based on Scripts.txt from Unicode Consortium.
    """
    global scripts,indexes
    if not indexes:
        for line in open(scriptfile).readlines():
            indexes.append(int(line[:5],16))
            scripts.append(line[6:-1])
    try:
        key = ord(char)
    except:
        key = ord(unicodedata.normalize("NFC",char))

# Linear search, 0.2ms per lookup
#    for index,script in lines:
#        if index > key:
#            return a 
#        a = script 

#Basic binary search, 0.01ms per lookup
#    max = len(lines)
#    min = 0
#    while not max == min:
#        test = (max + min) / 2
#        if lines[test][0] <= key:
#            if max == test + 1:
#                return lines[test][1]
#            min = test 
#        else:
#           max = test 
#    return lines[min][1]

    #Optimised bisection algorithm  0.001s per lookup
    return scripts[bisect.bisect_right(indexes, key)-1]


def inputloop():
    """
        Enter an interactive loop where the script of each character input (in utf-8) is printed.
    """
    while True:
        for char in raw_input().decode('utf-8'):
            print script(char)

if __name__ == "__main__":
    inputloop()
