import os

lines = []
scriptfile = os.path.dirname (os.path.abspath (__file__))+"/scripts.txt"

def script(char):
    """
        Get's the Unicode Script property of any character. Based on Scripts.txt from Unicode Consortium.
    """
    global lines
    if not lines:
        lines = [(int(x[:5],16), x[6:-1]) for x in open(scriptfile).readlines()]

    key = ord(char)

    for index,script in lines:
        if index > key:
            return a 
        a = script 
