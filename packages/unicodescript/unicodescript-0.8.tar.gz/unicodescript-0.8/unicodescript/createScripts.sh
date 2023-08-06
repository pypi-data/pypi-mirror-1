#!/bin/bash

# Converts the Unicode Consortium's Scripts.txt into our usable scripts.txt
cat Scripts.txt |\
 # Remove blank lines and comments
 grep "^[A-Z0-9]" |\
   #Remove everything except ranges and script name
   sed "s, #.*$,," |\
    #Pad all numbers to 5 hex chars
    sed "s,^\([A-Z0-9]\{4\}[ \.]\),0\1," |\
     sed "s,\.\([A-Z0-9]\{4\}[ \.]\),\.0\1," |\
      #Format singletons as lines
      sed "s,^\([A-Z0-9]*\) ,\1..\1 ," |\
       #Remove some excess whitespacing/formatting
       sed "s, *; *, ," |\

        sort  |\
         #Fill in the missing ranges with Xxxx
         python createScripts.py |\
          #Join contiguous ranges
          uniq --skip-chars=13 |\
           #Remove ends of ranges
           sed 's,\.\......,,' |\
            #Remove underscores
            sed 's,_, ,' |\
            #To stdout to proove we are doing something
             tee scripts.txt

