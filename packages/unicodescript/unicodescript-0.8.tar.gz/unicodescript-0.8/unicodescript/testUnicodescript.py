#!/usr/bin/python
# -*- coding: utf-8 -*-

# Due to bugs with the python interpreter, this may or may not work for you.
# It works in python2.5.2 UCS4 build on the SECOND run, as the .pyc file is read more correctly than the .py original

import unicodedata
import unicodescript

data={u'Common': [u'ˀ', u'’',  u'˥', u'', u'ː', u'˨', u'˩', u'�' , u'�'],  
      u'Latin:1': [u'éŵüớưāáøäēâȍɣʨëāåʉæžčä'],
   #   u'Latin:3': [u's̀', u'ọ̄', ],
      u'Greek': [u'ὕ', u'δ', u'ω', u'ρ', u'', u''],
      u'Cyrillic': [u'водаусгғобзыӡйхи'],
      u'Hebrew': [u'װַ', u'ר', u'ע', u'ס', u'א',  u'מ',u'י', u'ם', ],
      u'Arabic': [u'پ', u'ن', u'ی', u'ا', u'ب', u'آ', u'ۇ', u'س',  u'م',u'ا',u'ء', u'م',u'ي',u'ا',u'ه', u'ئاو', u'پاڻي', u'پانی', u'سۇ',],
      u'Bengali': [u'জ', u'ন'],
      u'Canadian Aboriginal': [u'ᓃ', u'ᐲ', u'ᔾ',  u'ᐃᒪᖅ'],
      u'Cherokee': [u'Ꭰ', u'Ꮉ'],
      u'Coptic': [u'ⲙ', u'ⲟ', u'ⲟ', u'ⲩ'],
      u'Cuneiform:1': [u'𒀀'], # Akkadian
      u'Devanagari': [u'प', u'ी', u'न', u'ा', u'ज', u'ल', u'पा', u'नी', u'आ', u'प', u'ब',  u'उदाक',  u'अम्म',u'पाणी', u'जल', u'अंब'],
      u'Ethiopic': [u'ማ', u'ይ', u'ው', u'ኃ'],
      u'Old Italic:1': [ u'𐌍', u'𐌉', u'𐌓', u'𐌄'], #Etruscan
      u'Georgian': [u'წ', u'ი', u'ლ', u'ყ', u'ა'],
      u'Gothic': [u'𐍅', u'𐌰', u'𐍄'],
      u'Gujarati': [u'પ', u'ણ', u'ા', u'ી', u'', u''],
      u'Gurmukhi': [u'ਪਾਣੀਜਲਆਬ', u'', u'', u'', u'', u''],
      u'Han': [u'水'],
      u'Cuneiform:2': [u'𒉿𒀀𒋫', u'', u'', u'', u'', u''], #Hittite
      u'Inherited': [u'̈'],
      u'Kannada': [u'ನೀರು', u'', u'', u'', u'', u''],
      u'Katakana': [u'ワ', u'カ', u'ッ'],
      u'Khmer': [u'ទឹក', u'', u'', u'', u'', u''],
      u'Linear B': [u'𐀈', u'𐀄', u'', u'', u'', u''], #Mycenian
      u'Lydian': [ u'𐤨𐤬𐤱𐤰', u'', u''],
      u'Malayalam': [u'ജലം', u'', u'', u'', u'', u''],
      u'Mongolian': [u'ᠮᡠᡴᡝ', u'ᠤᠰᠤᠨ', u'', u'', u'', u''],
      u'Myanmar': [u'ေ', u'ရ', u'ဍာ်',u'ထံ', u'ၼမ်ႉ', u'ဢႃႇပေႃႇ'],
      u'Oriya': [u'', u'ପାଣି', u'', u'', u'', u''],
      u'Phoenician': [u'𐤌𐤌', u'', u'', u'', u'', u''],
      u'Ol Chiki': [u'ᱫᱟᱜ', u'', u'', u'', u'', u''],
   #   u'Sindarin': [u'', u'', u'', u'', u'', u''],
      u'Sinhala': [u'ජලය', u'', u'', u'', u'', u''],
      u'Cuneiform:3': [u'𒀀', u'', u'', u'', u'', u''],#Sumerian
      u'Syriac': [u'ܡ', u'ܐ',  u'ܝ'],
      u'Tamil': [u'தண்ணீர்', u'', u'', u'', u'', u''],
      u'Telugu': [u'జము', u'ల'],
      u'Thaana': [u'ފެ', u'ން'],
      u'Thai': [u'น้', u'ำ'],
      u'Tibetan': [u'ཆུ'],
      u'Ugaritic': [u'𐎎', u'', u'', u'', u'', u''],
      u'Old Italic': [u'𐌖𐌕𐌖', u'', u'', u'', u'', u''], #Umbrian
      u'Yi': [u'ꒉ'],      
     }
if __name__ == "__main__":
  datasorted=sorted(data.keys())
  for script in datasorted:
    print script, 
    output=u'' ; flag = False
    for character in data[script]:
        character = character.encode('utf-8').decode('utf-8') # Work around for a bug in python2.5 UCS4 build which, when compiling a module treats UTTF-8 encoded characters outside the BMP as surrogate UTF-16 pairs
        # If we were to compile this module, and then import it and run it, it would work fine without this hack.
        if character:
            output+= character + u' '
            normalized=unicodedata.normalize('NFC', character)
            for n in normalized:
                s = unicodescript.script(n)
                output+= s + u' '
                if s == script.split(':')[0]:
                    output+= 'OK' + u' '
                else:
                    output+= 'FAILED' + u' ' + n + "(" + unicodescript.script(n) + ")"
                    flag= True
    if flag: print output
    else: print 'OK '+ "".join(data[script]).encode('utf-8')
