"""Functions to annotate and romanize (pinyin and zhuyin Unicode) Chinese text (numeric pin1yin1 or hanzi)."""

from os import path
try:
    from pysqlite2 import dbapi2 as _sqlite
except ImportError:
    try:
        import sqlite3 as _sqlite
    except ImportError:
        class DummySqlite(object):
            def connect(self, *args, **kwargs):
                raise NotImplementedError("Can't look up Chinese character without sqlite, please install pysqlite2 or upgrade to Python >=2.5")
        _sqlite = DummySqlite()

#TODO: add wade-giles, tongyong pinyin, yale, ... (http://www.pinyin.info/romanization/compare/zhuyin.html)
#TODO: try to find information on more exotic romanization schemes (e.g. "Latinxua Sinwenz")

## lookup tables / utility functions ####################################################

PINYIN = {'A0':u'A','A1':u'\u0100','A2':u'\xc1','A3':u'\u01cd','A4':u'\xc0','A5':u'A',
          'a0':u'a','a1':u'\u0101','a2':u'\xe1','a3':u'\u01ce','a4':u'\xe0','a5':u'a',
          'E0':u'E','E1':u'\u0112','E2':u'\xc9','E3':u'\u011a','E4':u'\xc8','E5':u'E',
          'e0':u'e','e1':u'\u0113','e2':u'\xe9','e3':u'\u011b','e4':u'\xe8','e5':u'e',
          'I0':u'I','I1':u'\u012a','I2':u'\xcd','I3':u'\u01cf','I4':u'\xcc','I5':u'I',
          'i0':u'i','i1':u'\u012b','i2':u'\xed','i3':u'\u01d0','i4':u'\xec','i5':u'i',
          'O0':u'O','O1':u'\u014c','O2':u'\xd3','O3':u'\u01d1','O4':u'\xd2','O5':u'O',
          'o0':u'o','o1':u'\u014d','o2':u'\xf3','o3':u'\u01d2','o4':u'\xf2','o5':u'o',
          'U0':u'U','U1':u'\u016a','U2':u'\xda','U3':u'\u01d3','U4':u'\xd9','U5':u'U',
          'u0':u'u','u1':u'\u016b','u2':u'\xfa','u3':u'\u01d4','u4':u'\xf9','u5':u'u',
          'V0':u'\u00dc','V1':u'\u01d5','V2':u'\u01d7','V3':u'\u01d9','V4':u'\u01db','V5':u'\u00dc',
          'v0':u'\u00fc','v1':u'\u01d6','v2':u'\u01d8','v3':u'\u01da','v4':u'\u01dc','v5':u'\u00fc'}

def lastvowel(s):
    '''Find the index of the last pinyin vowel (aeiouv) in string s.'''
    return max(map(s.rfind, 'aeiouv'))

## Pinyin text conversion #####################################################

def syllable_to_pinyin(syl):
    """Returns proper unicode string for one pinyin syllable + tone number (e.g. 'yi1')"""
    try:
        syl, tone = syl[:-1], int(syl[-1])
    except ValueError:
        #converting tone number to int failed, probably not a pinyin syllable
        return syl
    syl = syl.replace("u:", "v")
    if "a" in syl or "e" in syl:
        syl = syl.replace("a", PINYIN["a" + repr(tone)])
        syl = syl.replace("e", PINYIN["e" + repr(tone)])
    elif "ou" in syl:
        syl = syl.replace("o", PINYIN["o" + repr(tone)])
    else:
        vowel = syl[lastvowel(syl.lower())] #get the last vowel
        try:
            pinyin_unicode = PINYIN[vowel+repr(tone)]
            syl = syl.replace(vowel, pinyin_unicode)
        except KeyError:
            #couldn't find vowel+tone combination, probably not a pinyin syllable
            return syl+repr(tone) #return the original input
    if "v" in syl.lower():
        syl = syl.replace("v", PINYIN["v0"]).replace("V", PINYIN["V0"])
    return syl

def pinyin(pinyin_text):
    """Convert a numeric pinyin string (e.g. 'pin1yin1') to the proper Unicode characters"""
    syls = pinyin_text.strip().replace('1','1 ').replace('2','2 ').replace('3','3 ').replace('4','4 ').split()
    for syl in syls:
        newsyl = syllable_to_pinyin(syl)
        if syl == newsyl:
            #this isn't pinyin, don't do anything with it
            pass
        else:
            pinyin_text = pinyin_text.replace(syl, newsyl)
    return pinyin_text

## Pinyin to Zhuyin conversion ################################################

ZHUYIN_INITIALS_2 = {'zh': u'\u3113', 'ch': u'\u3114', 'sh': u'\u3115'}
ZHUYIN_INITIALS_1 = {'b': u'\u3105', 'p': u'\u3106', 'm': u'\u3107', 'f': u'\u3108',
                     'd': u'\u3109', 't': u'\u310a', 'n': u'\u310b', 'l': u'\u310c',
                     'g': u'\u310d', 'k': u'\u310e', 'h': u'\u310f',
                     'j': u'\u3110', 'q': u'\u3111', 'x': u'\u3112',
                     'r': u'\u3116',
                     'z': u'\u3117', 'c': u'\u3118', 's': u'\u3119',
                     'w': u'\u3128', 'y': u'\u3127'} #it is wrong to treat these as initials, but it simplifies the conversion

ZHUYIN_Y = {'ye':'ie', 'yi':'i', 'yong':'iong', 'you':'iu', 'yu':'v'}

ZHUYIN_FINALS = {'a':u'\u311a', 'o':u'\u311b', 'e':u'\u311c', 'ai':u'\u311e', 'ei':u'\u311f',
                 'ao':u'\u3120', 'ou':u'\u3121', 'an':u'\u3122', 'en':u'\u3123', 'ang':u'\u3124',
                 'eng':u'\u3125', 'i':u'\u3127', 'u':u'\u3128', 'er':u'\u3126',
                 #compound finals:
                 'ian':u'\u3127\u3122', 'iao':u'\u3127\u3120', 'ia':u'\u3127\u311a',
                 'ie':u'\u3127\u311d', 'in':u'\u3127\u3123', 'iu':u'\u3127\u3121',
                 'ing':u'\u3127\u3125', 'iang':u'\u3127\u3124', 'iong':u'\u3129\u3125',
                 'ong':u'\u3128\u3125',
                 'ua':u'\u3128\u311a', 'uai':u'\u3128\u311e', 'uan':u'\u3128\u3122',
                 'uang':u'\u3128\u3124', 'ui':u'\u3128\u311f', 'un':u'\u3128\u3123',
                 'uo':u'\u3128\u311b',
                 #u with umlaut:
                 'v':u'\u3129', 'van':u'\u3129\u3122', 've':u'\u3129\u311d', 'vn':u'\u3129\u3123'}

ZHUYIN_TONES = {'1':u'', '2':u'\u02ca', '3':u'\u02c7', '4':u'\u02cb', '5':u'\u02d9'}

def syllable_to_zhuyin(syllable):
    """Convert a single numeric pinyin syllable (e.g. "yi1") to a Zhuyin unicode string"""
    tone = ZHUYIN_TONES.get(syllable[-1], "")
    syllable = syllable.strip("12345").lower()

    xx = syllable[:2]
    out = ""

    #special cases
    if xx in ['ju', 'qu', 'xu']:
        syllable = syllable.replace('u', 'v') #the u vowel after j, q, x is actually u with umlaut
    elif syllable in ['zhi', 'chi', 'shi', 'ri', 'zi', 'ci', 'si', 'wu']:
        syllable = syllable[:-1] #remove the 'i' (or 'u' for 'wu'), only use the initial sound
    elif syllable[0] == 'y':
        if xx == 'yo':
            syllable = ZHUYIN_Y[syllable]
        elif xx in ZHUYIN_Y:
            syllable = syllable.replace(xx, ZHUYIN_Y[xx])

    #process initials (2 letter initials first)
    if xx in ZHUYIN_INITIALS_2:
        out += ZHUYIN_INITIALS_2[xx]
        syllable = syllable[2:]
    elif syllable[0] in ZHUYIN_INITIALS_1:
        out += ZHUYIN_INITIALS_1[syllable[0]]
        syllable = syllable[1:]

    #process finals
    if syllable in ZHUYIN_FINALS:
        out += ZHUYIN_FINALS[syllable]

    return out+tone

def zhuyin(pinyin_text):
    """Convert a numeric pinyin string (e.g. 'pin1yin1') to a Zhuyin unicode string"""
    syls = pinyin_text.strip().replace('1','1 ').replace('2','2 ').replace('3','3 ').replace('4','4 ').split()
    for syl in syls:
        newsyl = syllable_to_zhuyin(syl)
        if syl == newsyl:
            #this isn't pinyin, don't do anything with it
            pass
        else:
            pinyin_text = pinyin_text.replace(syl, newsyl)
    return pinyin_text

## Character annotation #######################################################

def zh_annotate_pinyin(zhtext, encoding='utf-8'):
    """Returns a list of annotated characters (with possible pinyin romanizations) for the input Chinese text"""
    con = _sqlite.connect(path.join(path.dirname(path.abspath(__file__)), 'data', 'cedict_zidianb.sqlite'))
    curs = con.cursor()

    if not isinstance(zhtext, unicode):
        zhtext = zhtext.decode(encoding)

    annotated = []
    for char in zhtext:
        if ord(char) > 256:
            #it's a UCN (like u'\u1234')
            curs.execute("SELECT ucn, pinyin FROM pinyin_lookup WHERE ucn=?", char)
            res = curs.fetchall()
            if len(res) == 1:
                #we have exactly one good result! (i.e. a match)
                ucn, syls = res[0]
                pinyins = sorted(syls.split())
                annotated.append((char, pinyins))
            else:
                #no record for this character
                annotated.append((char, [None]))
        else:
            #it's just a plain character
            if len(annotated) > 0 and isinstance(annotated[-1], basestring):
                #collapse multiple non-chinese characters into one string
                annotated[-1] += char
            else:
                #start a new string for non-chinese text
                annotated.append(char)
    return annotated
