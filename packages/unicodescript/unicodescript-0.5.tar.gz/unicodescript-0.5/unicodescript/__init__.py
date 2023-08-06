import os
import unicodedata

lines = []
scriptfile = os.path.dirname (os.path.abspath (__file__))+"/scripts.txt"

def script(char):
    """
        Gets the Unicode Script property of any character. Based on Scripts.txt from Unicode Consortium.
    """
    global lines
    if not lines:
        lines = [(int(x[:5],16), x[6:-1]) for x in open(scriptfile).readlines()]

    try:
        key = ord(char)
    except:
        key = ord(unicodedata.normalize("NFC",char))

    for index,script in lines:
        if index > key:
            return a 
        a = script 

def inputloop():
    while True:
        for char in raw_input().decode('utf-8'):
            print script(char)

if __name__ == "__main__":
    inputloop()
